// Telegram Account types
export interface TelegramAccountStartAuth {
  phone: string;
}

export interface StartAuthResponse {
  phone: string;
  phone_code_hash: string;
}

export interface TelegramAccountVerifyCode {
  phone: string;
  code: string;
  phone_code_hash: string;
}

export interface TelegramAccountResponse {
  id: string;
  tenant_id: string;
  phone: string;
  status: string;
  last_active_at: string | null;
  created_at: string;
}

export interface TelegramUserInfo {
  id: number;
  username: string | null;
  first_name: string | null;
  last_name: string | null;
  phone: string;
}

export interface TelegramAccountDetail {
  account: TelegramAccountResponse;
  telegram_user: TelegramUserInfo | null;
}

// Subscription (Channel/Chat) types
export interface SubscriptionCreate {
  telegram_account_id: string;
  tg_id: number;
  username?: string;
  title?: string;
  channel_type: string; // channel, chat, group
  tags?: string[];
}

export interface SubscriptionUpdate {
  is_active?: boolean;
  tags?: string[];
}

export interface SubscriptionResponse {
  id: string;
  tenant_id: string;
  channel_id: string;
  telegram_account_id: string;
  is_active: boolean;
  tags: string[];
  created_at: string;
  updated_at: string;
  // Channel data (from join)
  channel_tg_id: number;
  channel_username: string | null;
  channel_title: string | null;
  channel_type: string;
}

// Dialog (for selecting channels to monitor)
export interface DialogInfo {
  id: number;
  title: string;
  username: string | null;
  type: string;
  participants_count: number | null;
  is_channel: boolean;
  is_group: boolean;
}
