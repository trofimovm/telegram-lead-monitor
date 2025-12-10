/**
 * TypeScript типы для Rules (правила мониторинга).
 * Соответствуют Pydantic schemas из backend/app/schemas/rule.py
 */

/**
 * Базовый тип для Rule
 */
export interface RuleBase {
  name: string;
  description?: string | null;
  prompt: string;
  threshold: number; // 0.00-1.00
  channel_ids?: string[] | null; // UUID[], null = все каналы
  is_active: boolean;
  schedule?: Record<string, any> | null;
}

/**
 * Данные для создания правила
 */
export interface RuleCreate extends RuleBase {}

/**
 * Данные для обновления правила (все поля опциональны)
 */
export interface RuleUpdate {
  name?: string;
  description?: string | null;
  prompt?: string;
  threshold?: number;
  channel_ids?: string[] | null;
  is_active?: boolean;
  schedule?: Record<string, any> | null;
}

/**
 * Ответ API с данными правила
 */
export interface RuleResponse extends RuleBase {
  id: string;
  tenant_id: string;
  created_at: string;
  updated_at: string;
  leads_count?: number; // Количество найденных лидов
}

/**
 * Запрос на тестирование правила
 */
export interface RuleTestRequest {
  message_text: string;
}

/**
 * Результат тестирования правила
 */
export interface RuleTestResponse {
  is_match: boolean;
  confidence: number; // 0.0-1.0
  reasoning: string;
  would_create_lead: boolean;
  extracted_entities?: {
    contacts?: string[];
    keywords?: string[];
    budget?: string | null;
    deadline?: string | null;
    summary?: string;
  } | null;
}

/**
 * Форма для создания/редактирования правила (UI state)
 */
export interface RuleFormData {
  name: string;
  description: string;
  prompt: string;
  threshold: number;
  channel_ids: string[]; // Empty array = все каналы
  is_active: boolean;
}

/**
 * Состояние для тестирования правила (UI state)
 */
export interface RuleTestState {
  isOpen: boolean;
  isLoading: boolean;
  messageText: string;
  result: RuleTestResponse | null;
  error: string | null;
}
