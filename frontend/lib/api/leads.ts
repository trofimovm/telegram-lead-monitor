import { apiClient } from './client';
import {
  LeadResponse,
  LeadWithDetails,
  LeadUpdate,
  LeadStats,
  LeadListParams,
  LeadListResponse,
} from './lead-types';

/**
 * API клиент для работы с лидами
 */
export const leadsApi = {
  /**
   * Получить список лидов с фильтрацией и пагинацией
   */
  listLeads: async (params?: LeadListParams): Promise<LeadListResponse> => {
    // Формируем query parameters
    const queryParams: Record<string, any> = {};

    if (params?.status) {
      queryParams.status = params.status;
    }
    if (params?.rule_id) {
      queryParams.rule_id = params.rule_id;
    }
    if (params?.channel_id) {
      queryParams.channel_id = params.channel_id;
    }
    if (params?.assignee_id) {
      queryParams.assignee_id = params.assignee_id;
    }
    if (params?.min_score !== undefined) {
      queryParams.min_score = params.min_score;
    }
    if (params?.date_from) {
      queryParams.date_from = params.date_from;
    }
    if (params?.date_to) {
      queryParams.date_to = params.date_to;
    }
    if (params?.skip !== undefined) {
      queryParams.skip = params.skip;
    }
    if (params?.limit !== undefined) {
      queryParams.limit = params.limit;
    }

    return apiClient.get<LeadListResponse>('/leads', { params: queryParams });
  },

  /**
   * Получить статистику по лидам
   */
  getLeadStats: async (): Promise<LeadStats> => {
    return apiClient.get<LeadStats>('/leads/stats');
  },

  /**
   * Получить детальную информацию о лиде
   * Включает полные данные сообщения, источника, правила и assignee
   */
  getLead: async (leadId: string): Promise<LeadWithDetails> => {
    return apiClient.get<LeadWithDetails>(`/leads/${leadId}`);
  },

  /**
   * Обновить лид (статус, assignee)
   */
  updateLead: async (leadId: string, data: LeadUpdate): Promise<LeadResponse> => {
    return apiClient.patch<LeadResponse>(`/leads/${leadId}`, data);
  },

  /**
   * Удалить лид
   * ВНИМАНИЕ: Сообщение останется в БД, удалится только запись о лиде
   */
  deleteLead: async (leadId: string): Promise<void> => {
    return apiClient.delete<void>(`/leads/${leadId}`);
  },

  /**
   * Обновить статус лида (вспомогательный метод)
   */
  updateLeadStatus: async (leadId: string, status: string): Promise<LeadResponse> => {
    return apiClient.patch<LeadResponse>(`/leads/${leadId}`, { status });
  },

  /**
   * Назначить лид на пользователя (вспомогательный метод)
   */
  assignLead: async (leadId: string, assigneeId: string | null): Promise<LeadResponse> => {
    return apiClient.patch<LeadResponse>(`/leads/${leadId}`, { assignee_id: assigneeId });
  },
};
