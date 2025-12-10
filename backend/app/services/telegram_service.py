from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, Channel, Chat, User as TelegramUser
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from app.config import settings
from app.utils.encryption import encrypt_session, decrypt_session


class TelegramService:
    """
    Service for interacting with Telegram API using Telethon.
    """

    def __init__(self):
        self.api_id = settings.TELEGRAM_API_ID
        self.api_hash = settings.TELEGRAM_API_HASH
        self._clients: Dict[str, TelegramClient] = {}

    async def create_client(
        self,
        phone: str,
        session_string: Optional[str] = None
    ) -> TelegramClient:
        """
        Create a new Telegram client.

        Args:
            phone: Phone number
            session_string: Optional existing session string

        Returns:
            TelegramClient instance
        """
        if session_string:
            session = StringSession(session_string)
        else:
            session = StringSession()

        client = TelegramClient(
            session,
            self.api_id,
            self.api_hash,
            device_model="Telegram Lead Monitor",
            system_version="1.0",
            app_version="1.0",
        )

        await client.connect()
        return client

    async def start_auth(self, phone: str) -> Dict[str, Any]:
        """
        Start authentication process for a phone number.

        Args:
            phone: Phone number to authenticate

        Returns:
            Dictionary with phone_code_hash for verification
        """
        client = await self.create_client(phone)

        # Send code request
        result = await client.send_code_request(phone)

        # Store client temporarily for code verification
        self._clients[phone] = client

        return {
            "phone": phone,
            "phone_code_hash": result.phone_code_hash,
        }

    async def verify_code(
        self,
        phone: str,
        code: str,
        phone_code_hash: str
    ) -> str:
        """
        Verify authentication code and complete login.

        Args:
            phone: Phone number
            code: Verification code from SMS/Telegram
            phone_code_hash: Hash from start_auth

        Returns:
            Session string for storing

        Raises:
            Exception: If verification fails
        """
        client = self._clients.get(phone)
        if not client:
            raise Exception("Authentication session not found. Please start auth again.")

        try:
            # Sign in with code
            await client.sign_in(phone, code, phone_code_hash=phone_code_hash)

            # Get session string
            session_string = client.session.save()

            # Clean up temporary client storage
            del self._clients[phone]

            return session_string

        except Exception as e:
            # Clean up on error
            if phone in self._clients:
                del self._clients[phone]
            raise e

    async def get_client_from_session(self, session_encrypted: bytes) -> TelegramClient:
        """
        Get authenticated Telegram client from encrypted session.

        Args:
            session_encrypted: Encrypted session data

        Returns:
            Authenticated TelegramClient
        """
        session_string = decrypt_session(session_encrypted)
        client = TelegramClient(
            StringSession(session_string),
            self.api_id,
            self.api_hash,
        )
        await client.connect()

        if not await client.is_user_authorized():
            raise Exception("Session is not authorized")

        return client

    async def get_dialogs(
        self,
        session_encrypted: bytes,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get list of dialogs (chats, channels, groups) for authenticated user.

        Args:
            session_encrypted: Encrypted session data
            limit: Maximum number of dialogs to fetch

        Returns:
            List of dialog information
        """
        client = await self.get_client_from_session(session_encrypted)

        try:
            dialogs = await client.get_dialogs(limit=limit)

            result = []
            for dialog in dialogs:
                entity = dialog.entity

                dialog_info = {
                    "id": entity.id,
                    "title": getattr(entity, "title", None) or getattr(entity, "first_name", "Unknown"),
                    "username": getattr(entity, "username", None),
                    "type": self._get_entity_type(entity),
                    "participants_count": getattr(entity, "participants_count", None),
                    "is_channel": isinstance(entity, Channel) and entity.broadcast,
                    "is_group": isinstance(entity, Channel) and entity.megagroup,
                }

                result.append(dialog_info)

            return result

        finally:
            await client.disconnect()

    async def get_channel_messages(
        self,
        session_encrypted: bytes,
        channel_id: int,
        limit: int = 100,
        offset_id: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get messages from a channel.

        Args:
            session_encrypted: Encrypted session data
            channel_id: Telegram channel ID
            limit: Maximum number of messages to fetch
            offset_id: Message ID to start from (for pagination)

        Returns:
            List of message information
        """
        client = await self.get_client_from_session(session_encrypted)

        try:
            # Get channel entity
            channel = await client.get_entity(channel_id)

            # Get messages
            messages = await client.get_messages(
                channel,
                limit=limit,
                offset_id=offset_id
            )

            result = []
            for msg in messages:
                if msg.message:  # Only text messages for now
                    message_info = {
                        "id": msg.id,
                        "text": msg.message,
                        "date": msg.date.isoformat(),
                        "views": msg.views,
                        "forwards": msg.forwards,
                        "author": None,
                    }

                    # Try to get author info
                    if msg.sender:
                        sender = msg.sender
                        message_info["author"] = {
                            "id": sender.id,
                            "username": getattr(sender, "username", None),
                            "first_name": getattr(sender, "first_name", None),
                        }

                    result.append(message_info)

            return result

        finally:
            await client.disconnect()

    async def get_me(self, session_encrypted: bytes) -> Dict[str, Any]:
        """
        Get information about the authenticated user.

        Args:
            session_encrypted: Encrypted session data

        Returns:
            User information
        """
        client = await self.get_client_from_session(session_encrypted)

        try:
            me = await client.get_me()

            return {
                "id": me.id,
                "username": me.username,
                "first_name": me.first_name,
                "last_name": me.last_name,
                "phone": me.phone,
            }

        finally:
            await client.disconnect()

    def _get_entity_type(self, entity) -> str:
        """
        Determine entity type.

        Args:
            entity: Telegram entity

        Returns:
            Entity type as string
        """
        if isinstance(entity, Channel):
            if entity.broadcast:
                return "channel"
            elif entity.megagroup:
                return "group"
            else:
                return "chat"
        elif isinstance(entity, Chat):
            return "chat"
        elif isinstance(entity, TelegramUser):
            return "user"
        else:
            return "unknown"


# Global instance
telegram_service = TelegramService()
