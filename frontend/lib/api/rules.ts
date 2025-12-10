import { apiClient } from './client';
import {
  RuleCreate,
  RuleUpdate,
  RuleResponse,
  RuleTestRequest,
  RuleTestResponse,
} from './rule-types';

/**
 * API клиент для работы с правилами мониторинга
 */
export const rulesApi = {
  /**
   * Создать новое правило
   */
  createRule: async (data: RuleCreate): Promise<RuleResponse> => {
    return apiClient.post<RuleResponse>('/rules', data);
  },

  /**
   * Получить список правил
   * @param isActive - Фильтр по активности (опционально)
   */
  listRules: async (isActive?: boolean): Promise<RuleResponse[]> => {
    const params = isActive !== undefined ? { is_active: isActive } : {};
    return apiClient.get<RuleResponse[]>('/rules', { params });
  },

  /**
   * Получить детали правила по ID
   */
  getRule: async (ruleId: string): Promise<RuleResponse> => {
    return apiClient.get<RuleResponse>(`/rules/${ruleId}`);
  },

  /**
   * Обновить правило
   */
  updateRule: async (ruleId: string, data: RuleUpdate): Promise<RuleResponse> => {
    return apiClient.patch<RuleResponse>(`/rules/${ruleId}`, data);
  },

  /**
   * Удалить правило
   * ВНИМАНИЕ: Все связанные лиды также будут удалены (cascade)
   */
  deleteRule: async (ruleId: string): Promise<void> => {
    return apiClient.delete<void>(`/rules/${ruleId}`);
  },

  /**
   * Протестировать правило на примере сообщения
   * Возвращает результат анализа LLM без сохранения в БД
   */
  testRule: async (ruleId: string, data: RuleTestRequest): Promise<RuleTestResponse> => {
    return apiClient.post<RuleTestResponse>(`/rules/${ruleId}/test`, data);
  },

  /**
   * Toggle активности правила (вспомогательный метод)
   */
  toggleRuleActive: async (ruleId: string, isActive: boolean): Promise<RuleResponse> => {
    return apiClient.patch<RuleResponse>(`/rules/${ruleId}`, { is_active: isActive });
  },
};
