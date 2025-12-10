export type Language = 'en' | 'ru';

export interface Translations {
  // Navigation
  nav: {
    dashboard: string;
    telegramAccounts: string;
    sources: string;
    rules: string;
    leads: string;
    analytics: string;
    settings: string;
  };

  // User menu
  user: {
    editProfile: string;
    signOut: string;
  };

  // Theme
  theme: {
    light: string;
    dark: string;
    system: string;
  };

  // Dashboard
  dashboard: {
    welcome: string;
    welcomeBack: string;
    subtitle: string;
    activeSources: string;
    activeSourcesDesc: string;
    activeRules: string;
    activeRulesDesc: string;
    totalLeads: string;
    totalLeadsDesc: string;
    recentLeads: string;
    recentLeadsDesc: string;
    activityTrends: string;
    activityTrendsDesc: string;
    viewAnalytics: string;
    leadsCreated: string;
    messagesCollected: string;
    conversionRate: string;
    vsPreviously: string;
    leadsByStatus: string;
    leadsByStatusDesc: string;
    recentLeadsWidget: string;
    recentLeadsWidgetDesc: string;
    viewAll: string;
  };

  // Quick Actions
  quickActions: {
    title: string;
    subtitle: string;
    step1Title: string;
    step1Desc: string;
    step1Button: string;
    step2Title: string;
    step2Desc: string;
    step2Button: string;
    step3Title: string;
    step3Desc: string;
    step3Button: string;
    step4Title: string;
    step4Desc: string;
    step4Button: string;
    connectTelegram: string;
    connectTelegramDesc: string;
    manageAccounts: string;
    addSources: string;
    addSourcesDesc: string;
    manageSources: string;
    createRules: string;
    createRulesDesc: string;
    manageRules: string;
    reviewLeads: string;
    reviewLeadsDesc: string;
    viewLeads: string;
  };

  // Profile
  profile: {
    title: string;
    subtitle: string;
    fullName: string;
    fullNamePlaceholder: string;
    email: string;
    emailPlaceholder: string;
    company: string;
    companyPlaceholder: string;
    companyHint: string;
    phone: string;
    phonePlaceholder: string;
    phoneHint: string;
    editProfile: string;
    saveChanges: string;
    cancel: string;
    saving: string;
    accountInfo: string;
    accountStatus: string;
    emailVerified: string;
    memberSince: string;
    active: string;
    inactive: string;
    yes: string;
    no: string;
  };

  // Telegram Accounts (extended)
  telegramAccounts: {
    title: string;
    subtitle: string;
    addAccount: string;
    noAccountsTitle: string;
    noAccountsDesc: string;
    addFirstAccount: string;
    status: string;
    connected: string;
    lastActive: string;
    viewSources: string;
    disconnect: string;

    // Modal
    addAccountModal: string;
    enterPhoneDesc: string;
    enterCodeDesc: string;
    phoneNumber: string;
    phonePlaceholder: string;
    verificationCode: string;
    codePlaceholder: string;
    cancel: string;
    sendCode: string;
    verify: string;
    codeSentTo: string;

    // Validation & errors
    enterPhone: string;
    enterCode: string;
    disconnectConfirm: string;
    failedToLoad: string;
    failedToSendCode: string;
    failedToVerify: string;
    failedToDelete: string;
  };

  // Sources
  sources: {
    title: string;
    subtitle: string;
    addSource: string;
    addModalTitle: string;
    addModalDesc: string;
    addSourceButton: string;
    selectAccount: string;
    selectChannelOrGroup: string;
    noChannelsFound: string;
    channel: string;
    group: string;
    members: string;
    connectAccountFirst: string;
    noSources: string;
    noSourcesDesc: string;
    addFirstSource: string;
    unnamed: string;
    subscribers: string;
    type: string;
    added: string;
    pause: string;
    activate: string;
    remove: string;
    active: string;
    paused: string;
    confirmDelete: string;
    failedToLoad: string;
    failedToLoadChannels: string;
    selectChannel: string;
    failedToAdd: string;
    failedToUpdate: string;
    failedToDelete: string;
  };

  // Leads (extended)
  leads: {
    title: string;
    subtitle: string;
    status: string;
    allStatuses: string;
    rule: string;
    allRules: string;
    source: string;
    allSources: string;
    exportCSV: string;
    exporting: string;
    noLeads: string;
    noLeadsDesc: string;
    tryAdjustingFilters: string;
    filters: string;
    resetFilters: string;
    score: string;
    viewDetails: string;
    showing: string;
    previous: string;
    next: string;

    // Detail modal
    leadDetails: string;
    completeInformation: string;
    confidenceScore: string;
    created: string;
    message: string;
    views: string;
    links: string;
    llmAnalysis: string;
    extractedInformation: string;
    contacts: string;
    keywords: string;
    budget: string;
    deadline: string;
    matchedRule: string;
    openInTelegram: string;
    deleteConfirm: string;
    totalLeads: string;
    foundLeads: string;
  };

  // Rules
  rules: {
    title: string;
    subtitle: string;
    addRule: string;
    noRules: string;
    noRulesDesc: string;
    createFirstRule: string;
    editRule: string;
    addNewRule: string;
    createRulesDesc: string;
    ruleFormDesc: string;
    noDescription: string;

    // Form fields
    ruleName: string;
    ruleNamePlaceholder: string;
    description: string;
    descriptionOptional: string;
    descriptionPlaceholder: string;
    llmPrompt: string;
    llmPromptPlaceholder: string;
    llmPromptHint: string;
    confidenceThreshold: string;
    confidenceThresholdHint: string;
    applyToSources: string;
    applyToSourcesHint: string;
    noSourcesAvailable: string;
    addChannelsFirst: string;
    activeStartImmediately: string;

    // Card labels
    threshold: string;
    sources: string;
    selectedSources: string;
    sourcesSelected: string;
    allSources: string;
    leadsFound: string;

    // Status badges
    active: string;
    paused: string;

    // Actions
    edit: string;
    test: string;
    testRule: string;
    activate: string;
    pause: string;
    delete: string;

    // Test modal
    testRuleTitle: string;
    testRuleDesc: string;
    sampleMessage: string;
    sampleMessagePlaceholder: string;
    match: string;
    yes: string;
    no: string;
    confidence: string;
    wouldCreateLead: string;
    llmReasoning: string;
    extractedEntities: string;
    contacts: string;
    keywords: string;
    budget: string;
    deadline: string;

    // Validation & errors
    enterRuleName: string;
    enterPrompt: string;
    enterTestMessage: string;
    confirmDelete: string;
    deleteConfirm: string;
    saveChanges: string;
    createRule: string;
    failedToLoad: string;
    failedToSave: string;
    failedToDelete: string;
    failedToUpdate: string;
    failedToTest: string;
  };

  // Analytics
  analytics: {
    title: string;
    subtitle: string;
    loadingAnalytics: string;

    // Summary cards
    totalLeads: string;
    last30Days: string;
    messagesCollected: string;
    conversion: string;
    messagesToLeads: string;
    avgScore: string;
    leadQuality: string;

    // Activity trends
    activityTrends: string;
    period: string;
    previous: string;

    // Time series
    leadsOverTime: string;

    // Conversion funnel
    conversionFunnel: string;
    totalConversion: string;
    leads: string;
    conversionRate: string;

    // Top performers
    topSource: string;
    mostLeads: string;
    topRule: string;

    // Performance tables
    sourcePerformance: string;
    topSources: string;
    source: string;
    messages: string;

    rulePerformance: string;
    allRules: string;
    rule: string;
    totalLeadsLabel: string;
    last7Days: string;
    last30DaysLabel: string;
    status: string;
    active: string;
    inactive: string;
  };

  // Settings
  settings: {
    title: string;
    subtitle: string;

    // Notifications section
    notificationSettings: string;
    notificationSettingsDesc: string;

    // Global toggles
    emailNotifications: string;
    emailNotificationsDesc: string;
    inAppNotifications: string;
    inAppNotificationsDesc: string;

    // Event types
    eventTypes: string;
    newLeads: string;
    newLeadsDesc: string;
    leadStatusChange: string;
    leadStatusChangeDesc: string;
    leadAssignment: string;
    leadAssignmentDesc: string;

    // Actions
    saveSettings: string;
    saving: string;

    // Messages
    loadingSettings: string;
    settingsSaved: string;
    failedToLoad: string;
    failedToSave: string;
  };

  // Notifications
  notifications: {
    title: string;
    markAllRead: string;
    loading: string;
    noNotifications: string;
    markRead: string;
    viewAll: string;
  };

  // Time labels
  time: {
    justNow: string;
    minutesAgo: string;
    hoursAgo: string;
    daysAgo: string;
  };

  // Lead Status (from API)
  leadStatus: {
    new: string;
    in_progress: string;
    processed: string;
    archived: string;
  };

  // Notification Type (from API)
  notificationType: {
    leadCreated: string;
    leadStatusChanged: string;
    leadAssigned: string;
    ruleTriggered: string;
    system: string;
  };

  // Breadcrumbs (extended)
  breadcrumbs: {
    home: string;
    dashboard: string;
    telegramAccounts: string;
    sources: string;
    rules: string;
    leads: string;
    analytics: string;
    settings: string;
    profile: string;
  };

  // Charts
  charts: {
    noData: string;
  };

  // Common (extended)
  common: {
    loading: string;
    error: string;
    success: string;
    save: string;
    cancel: string;
    delete: string;
    edit: string;
    close: string;
    back: string;
    yes: string;
    no: string;
    active: string;
    inactive: string;
    confirm: string;
    search: string;
    filter: string;
    sort: string;
    showing: string;
    of: string;
    items: string;
    noDataAvailable: string;
    somethingWentWrong: string;
    tryAgain: string;
    areYouSure: string;
  };
}

export const translations: Record<Language, Translations> = {
  en: {
    nav: {
      dashboard: 'Dashboard',
      telegramAccounts: 'Telegram Accounts',
      sources: 'Sources',
      rules: 'Rules',
      leads: 'Leads',
      analytics: 'Analytics',
      settings: 'Settings',
    },
    user: {
      editProfile: 'Edit Profile',
      signOut: 'Sign Out',
    },
    theme: {
      light: 'Light',
      dark: 'Dark',
      system: 'System',
    },
    dashboard: {
      welcome: 'Welcome back',
      welcomeBack: 'Welcome back, {{name}}!',
      subtitle: "Here's what's happening with your Telegram lead monitoring.",
      activeSources: 'Active Sources',
      activeSourcesDesc: 'Telegram channels being monitored',
      activeRules: 'Active Rules',
      activeRulesDesc: 'Monitoring rules configured',
      totalLeads: 'Total Leads',
      totalLeadsDesc: 'All time leads found',
      recentLeads: 'Recent Leads',
      recentLeadsDesc: 'Last 24 hours',
      activityTrends: 'Activity Trends',
      activityTrendsDesc: 'Last 7 days vs Previous 7 days',
      viewAnalytics: 'View Analytics',
      leadsCreated: 'Leads Created',
      messagesCollected: 'Messages Collected',
      conversionRate: 'Conversion Rate',
      vsPreviously: 'vs {{value}} previously',
      leadsByStatus: 'Leads by Status',
      leadsByStatusDesc: 'Distribution of leads across statuses',
      recentLeadsWidget: 'Recent Leads',
      recentLeadsWidgetDesc: 'Your most recent leads',
      viewAll: 'View All',
    },
    quickActions: {
      title: 'Quick Actions',
      subtitle: 'Get started with these essential steps',
      step1Title: 'Connect Telegram Account',
      step1Desc: 'Add your Telegram account to access channels',
      step1Button: 'Connect Account',
      step2Title: 'Add Sources',
      step2Desc: 'Select channels and groups to monitor',
      step2Button: 'Add Sources',
      step3Title: 'Create Rules',
      step3Desc: 'Set up monitoring rules with AI',
      step3Button: 'Create Rules',
      step4Title: 'Review Leads',
      step4Desc: 'Check your found leads',
      step4Button: 'View Leads',
      connectTelegram: 'Connect Telegram Accounts',
      connectTelegramDesc: 'Add your Telegram accounts to access channels and chats',
      manageAccounts: 'Manage Accounts',
      addSources: 'Add Monitoring Sources',
      addSourcesDesc: 'Select Telegram channels or groups to monitor for leads',
      manageSources: 'Manage Sources',
      createRules: 'Create Monitoring Rules',
      createRulesDesc: 'Define LLM-powered rules to automatically find relevant leads',
      manageRules: 'Manage Rules',
      reviewLeads: 'Review Your Leads',
      reviewLeadsDesc: 'View and manage leads found by your monitoring rules',
      viewLeads: 'View Leads',
    },
    profile: {
      title: 'Profile Settings',
      subtitle: 'Manage your personal information and account settings',
      fullName: 'Full Name',
      fullNamePlaceholder: 'Enter your full name',
      email: 'Email Address',
      emailPlaceholder: 'Enter your email',
      company: 'Company',
      companyPlaceholder: 'Enter your company name',
      companyHint: 'Optional: Your company or organization name',
      phone: 'Phone Number',
      phonePlaceholder: 'Enter your phone number',
      phoneHint: 'Optional: Your contact phone number',
      editProfile: 'Edit Profile',
      saveChanges: 'Save Changes',
      cancel: 'Cancel',
      saving: 'Saving...',
      accountInfo: 'Account Information',
      accountStatus: 'Account Status:',
      emailVerified: 'Email Verified:',
      memberSince: 'Member Since:',
      active: 'Active',
      inactive: 'Inactive',
      yes: 'Yes',
      no: 'No',
    },
    telegramAccounts: {
      title: 'Telegram Accounts',
      subtitle: 'Connect your Telegram accounts to monitor channels and chats',
      addAccount: '+ Add Account',
      noAccountsTitle: 'No Telegram accounts connected',
      noAccountsDesc: 'Connect your first Telegram account to start monitoring channels',
      addFirstAccount: 'Add Your First Account',
      status: 'Status:',
      connected: 'Connected:',
      lastActive: 'Last active:',
      viewSources: 'View Sources',
      disconnect: 'Disconnect',

      // Modal
      addAccountModal: 'Add Telegram Account',
      enterPhoneDesc: 'Enter your phone number to receive a verification code',
      enterCodeDesc: 'Enter the verification code sent to your Telegram app',
      phoneNumber: 'Phone Number',
      phonePlaceholder: '+1234567890',
      verificationCode: 'Verification Code',
      codePlaceholder: '12345',
      cancel: 'Cancel',
      sendCode: 'Send Code',
      verify: 'Verify',
      codeSentTo: 'Verification code sent to {{phone}}',

      // Validation & errors
      enterPhone: 'Please enter phone number',
      enterCode: 'Please enter verification code',
      disconnectConfirm: 'Are you sure you want to disconnect this Telegram account?',
      failedToLoad: 'Failed to load accounts',
      failedToSendCode: 'Failed to send code',
      failedToVerify: 'Failed to verify code',
      failedToDelete: 'Failed to delete account',
    },
    sources: {
      title: 'Monitoring Sources',
      subtitle: "Telegram channels and groups you're monitoring for leads",
      addSource: '+ Add Source',
      type: 'Type:',
      added: 'Added:',
      pause: 'Pause',
      remove: 'Remove',
      active: 'Active',
    },
    leads: {
      title: 'Leads',
      subtitle: 'Messages that matched your monitoring rules',
      status: 'Status',
      allStatuses: 'All Statuses',
      rule: 'Rule',
      allRules: 'All Rules',
      source: 'Source',
      allSources: 'All Sources',
      exportCSV: 'Export to CSV',
      exporting: 'Exporting...',
      noLeads: 'No leads found',
      noLeadsDesc: 'Leads will appear here when messages match your rules',
      tryAdjustingFilters: 'Try adjusting your filters',
      filters: 'Filters',
      resetFilters: 'Reset Filters',
      score: 'Score',
      viewDetails: 'View Details',
      showing: 'Showing',
      previous: 'Previous',
      next: 'Next',

      // Detail modal
      leadDetails: 'Lead Details',
      completeInformation: 'Complete information about this lead',
      confidenceScore: 'Confidence Score',
      created: 'Created',
      message: 'Message',
      views: 'Views',
      links: 'Links',
      llmAnalysis: 'LLM Analysis',
      extractedInformation: 'Extracted Information',
      contacts: 'Contacts',
      keywords: 'Keywords',
      budget: 'Budget',
      deadline: 'Deadline',
      matchedRule: 'Matched Rule',
      openInTelegram: 'Open in Telegram',
      deleteConfirm: 'Are you sure you want to delete this lead?',
      totalLeads: 'Total Leads',
      foundLeads: 'Found',
    },
    rules: {
      title: 'Monitoring Rules',
      subtitle: 'LLM-powered rules for finding relevant leads in Telegram messages',
      addRule: '+ Add Rule',
      noRules: 'No rules created yet',
      noRulesDesc: 'Create your first monitoring rule to start finding leads',
      createFirstRule: 'Create Your First Rule',
      editRule: 'Edit Rule',
      addNewRule: 'Add New Rule',
      createRulesDesc: 'Create LLM-powered rules to automatically find relevant leads',
      ruleFormDesc: 'Fill in the details to create a new monitoring rule',
      noDescription: 'No description provided',

      // Form fields
      ruleName: 'Rule Name',
      ruleNamePlaceholder: 'e.g., Python Developer Jobs',
      description: 'Description',
      descriptionOptional: 'Description (optional)',
      descriptionPlaceholder: 'Brief description of what this rule looks for',
      llmPrompt: 'LLM Prompt',
      llmPromptPlaceholder: 'Describe what kind of messages you\'re looking for. Be specific about criteria, keywords, context, etc.\n\nExample: "Find messages where someone is looking for a Python developer with Django experience, mentions a budget above $100k, and needs to start within 1-2 months."',
      llmPromptHint: 'This prompt will be used by LLM to analyze messages',
      confidenceThreshold: 'Confidence Threshold',
      confidenceThresholdHint: 'Minimum LLM confidence score to create a lead (higher = fewer but more relevant leads)',
      applyToSources: 'Apply to Sources',
      applyToSourcesHint: 'Select specific sources or leave empty to apply to all sources',
      noSourcesAvailable: 'No sources available. Add Telegram channels first.',
      addChannelsFirst: 'Add Telegram channels first.',
      activeStartImmediately: 'Active (start monitoring immediately)',

      // Card labels
      threshold: 'Threshold',
      sources: 'Sources',
      selectedSources: 'selected',
      sourcesSelected: '{{count}} sources selected',
      allSources: 'All sources',
      leadsFound: 'Leads found',

      // Status badges
      active: 'Active',
      paused: 'Paused',

      // Actions
      edit: 'Edit',
      test: 'Test',
      testRule: 'Test Rule',
      activate: 'Activate',
      pause: 'Pause',
      delete: 'Delete',

      // Test modal
      testRuleTitle: 'Test Rule',
      testRuleDesc: 'Test how this rule would analyze a sample message',
      sampleMessage: 'Sample Message',
      sampleMessagePlaceholder: 'Paste a message to test against this rule...',
      match: 'Match',
      yes: 'Yes',
      no: 'No',
      confidence: 'Confidence',
      wouldCreateLead: 'Would Create Lead',
      llmReasoning: 'LLM Reasoning',
      extractedEntities: 'Extracted Entities',
      contacts: 'Contacts',
      keywords: 'Keywords',
      budget: 'Budget',
      deadline: 'Deadline',

      // Validation & errors
      enterRuleName: 'Please enter a rule name',
      enterPrompt: 'Please enter a prompt (at least 10 characters)',
      enterTestMessage: 'Please enter a message to test',
      confirmDelete: 'Are you sure? All associated leads will also be deleted.',
      deleteConfirm: 'Are you sure? All associated leads will also be deleted.',
      saveChanges: 'Save Changes',
      createRule: 'Create Rule',
      failedToLoad: 'Failed to load rules',
      failedToSave: 'Failed to save rule',
      failedToDelete: 'Failed to delete rule',
      failedToUpdate: 'Failed to update rule',
      failedToTest: 'Failed to test rule',
    },
    analytics: {
      title: 'Analytics',
      subtitle: 'Detailed statistics and metrics of your monitoring system',
      loadingAnalytics: 'Loading analytics...',

      // Summary cards
      totalLeads: 'Total Leads',
      last30Days: 'Last 30 days',
      messagesCollected: 'Messages Collected',
      conversion: 'Conversion',
      messagesToLeads: 'Messages → Leads',
      avgScore: 'Avg Score',
      leadQuality: 'Lead Quality',

      // Activity trends
      activityTrends: 'Activity Trends',
      period: 'Period',
      previous: 'Previous',

      // Time series
      leadsOverTime: 'Lead creation over time',

      // Conversion funnel
      conversionFunnel: 'Conversion Funnel',
      totalConversion: 'Total conversion',
      leads: 'leads',
      conversionRate: 'conversion',

      // Top performers
      topSource: 'Top Source',
      mostLeads: 'Most leads',
      topRule: 'Top Rule',

      // Performance tables
      sourcePerformance: 'Source Performance',
      topSources: 'Top sources',
      source: 'Source',
      messages: 'Messages',

      rulePerformance: 'Rule Performance',
      allRules: 'All rules and their effectiveness',
      rule: 'Rule',
      totalLeadsLabel: 'Total Leads',
      last7Days: '7d',
      last30DaysLabel: '30d',
      status: 'Status',
      active: 'Active',
      inactive: 'Inactive',
    },
    settings: {
      title: 'Settings',
      subtitle: 'Manage notifications and account settings',

      // Notifications section
      notificationSettings: 'Notification Settings',
      notificationSettingsDesc: 'Choose which notifications you want to receive',

      // Global toggles
      emailNotifications: 'Email Notifications',
      emailNotificationsDesc: 'Receive notifications via email',
      inAppNotifications: 'In-app Notifications',
      inAppNotificationsDesc: 'Show notifications in the app (bell icon in header)',

      // Event types
      eventTypes: 'Event Types',
      newLeads: 'New Leads',
      newLeadsDesc: 'Notify when the system finds a new lead matching your rules',
      leadStatusChange: 'Lead Status Change',
      leadStatusChangeDesc: 'Notify when a lead status changes (new → in progress → processed)',
      leadAssignment: 'Lead Assignment',
      leadAssignmentDesc: 'Notify when a lead is assigned to you',

      // Actions
      saveSettings: 'Save Settings',
      saving: 'Saving...',

      // Messages
      loadingSettings: 'Loading settings...',
      settingsSaved: 'Settings saved successfully!',
      failedToLoad: 'Failed to load settings',
      failedToSave: 'Failed to save settings',
    },
    notifications: {
      title: 'Notifications',
      markAllRead: 'Mark all as read',
      loading: 'Loading...',
      noNotifications: 'No notifications',
      markRead: 'Mark as read',
      viewAll: 'View all notifications',
    },
    time: {
      justNow: 'just now',
      minutesAgo: '{{count}}m ago',
      hoursAgo: '{{count}}h ago',
      daysAgo: '{{count}}d ago',
    },
    leadStatus: {
      new: 'New',
      in_progress: 'In Progress',
      processed: 'Processed',
      archived: 'Archived',
    },
    notificationType: {
      leadCreated: 'New Lead',
      leadStatusChanged: 'Status Changed',
      leadAssigned: 'Lead Assignment',
      ruleTriggered: 'Rule Triggered',
      system: 'System',
    },
    breadcrumbs: {
      home: 'Home',
      dashboard: 'Dashboard',
      telegramAccounts: 'Telegram Accounts',
      sources: 'Sources',
      rules: 'Rules',
      leads: 'Leads',
      analytics: 'Analytics',
      settings: 'Settings',
      profile: 'Profile',
    },
    charts: {
      noData: 'No data to display',
    },
    common: {
      loading: 'Loading...',
      error: 'Error',
      success: 'Success',
      save: 'Save',
      cancel: 'Cancel',
      delete: 'Delete',
      edit: 'Edit',
      close: 'Close',
      back: 'Back',
      yes: 'Yes',
      no: 'No',
      active: 'Active',
      inactive: 'Inactive',
      confirm: 'Confirm',
      search: 'Search',
      filter: 'Filter',
      sort: 'Sort',
      showing: 'Showing',
      of: 'of',
      items: 'items',
      noDataAvailable: 'No data available',
      somethingWentWrong: 'Something went wrong',
      tryAgain: 'Try again',
      areYouSure: 'Are you sure?',
    },
  },
  ru: {
    nav: {
      dashboard: 'Дашборд',
      telegramAccounts: 'Telegram Аккаунты',
      sources: 'Источники',
      rules: 'Правила',
      leads: 'Лиды',
      analytics: 'Аналитика',
      settings: 'Настройки',
    },
    user: {
      editProfile: 'Редактировать профиль',
      signOut: 'Выйти',
    },
    theme: {
      light: 'Светлая',
      dark: 'Темная',
      system: 'Системная',
    },
    dashboard: {
      welcome: 'С возвращением',
      welcomeBack: 'С возвращением, {{name}}!',
      subtitle: 'Вот что происходит с вашим мониторингом Telegram лидов.',
      activeSources: 'Активные источники',
      activeSourcesDesc: 'Отслеживаемые Telegram каналы',
      activeRules: 'Активные правила',
      activeRulesDesc: 'Настроенные правила мониторинга',
      totalLeads: 'Всего лидов',
      totalLeadsDesc: 'Все найденные лиды',
      recentLeads: 'Недавние лиды',
      recentLeadsDesc: 'За последние 24 часа',
      activityTrends: 'Тренды активности',
      activityTrendsDesc: 'Последние 7 дней vs Предыдущие 7 дней',
      viewAnalytics: 'Смотреть аналитику',
      leadsCreated: 'Создано лидов',
      messagesCollected: 'Собрано сообщений',
      conversionRate: 'Конверсия',
      vsPreviously: 'vs {{value}} ранее',
      leadsByStatus: 'Лиды по статусам',
      leadsByStatusDesc: 'Распределение лидов по статусам',
      recentLeadsWidget: 'Недавние лиды',
      recentLeadsWidgetDesc: 'Ваши последние лиды',
      viewAll: 'Показать все',
    },
    quickActions: {
      title: 'Быстрые действия',
      subtitle: 'Начните с этих важных шагов',
      step1Title: 'Подключить Telegram аккаунт',
      step1Desc: 'Добавьте Telegram аккаунт для доступа к каналам',
      step1Button: 'Подключить аккаунт',
      step2Title: 'Добавить источники',
      step2Desc: 'Выберите каналы и группы для мониторинга',
      step2Button: 'Добавить источники',
      step3Title: 'Создать правила',
      step3Desc: 'Настройте правила мониторинга с AI',
      step3Button: 'Создать правила',
      step4Title: 'Проверить лиды',
      step4Desc: 'Просмотрите найденные лиды',
      step4Button: 'Смотреть лиды',
      connectTelegram: 'Подключить Telegram аккаунты',
      connectTelegramDesc: 'Добавьте Telegram аккаунты для доступа к каналам и чатам',
      manageAccounts: 'Управление аккаунтами',
      addSources: 'Добавить источники мониторинга',
      addSourcesDesc: 'Выберите Telegram каналы или группы для мониторинга лидов',
      manageSources: 'Управление источниками',
      createRules: 'Создать правила мониторинга',
      createRulesDesc: 'Определите правила на основе LLM для автоматического поиска релевантных лидов',
      manageRules: 'Управление правилами',
      reviewLeads: 'Просмотреть ваши лиды',
      reviewLeadsDesc: 'Просматривайте и управляйте лидами, найденными вашими правилами мониторинга',
      viewLeads: 'Смотреть лиды',
    },
    profile: {
      title: 'Настройки профиля',
      subtitle: 'Управляйте вашей личной информацией и настройками аккаунта',
      fullName: 'Полное имя',
      fullNamePlaceholder: 'Введите ваше полное имя',
      email: 'Email адрес',
      emailPlaceholder: 'Введите ваш email',
      company: 'Компания',
      companyPlaceholder: 'Введите название компании',
      companyHint: 'Опционально: Название вашей компании или организации',
      phone: 'Номер телефона',
      phonePlaceholder: 'Введите ваш номер телефона',
      phoneHint: 'Опционально: Ваш контактный номер телефона',
      editProfile: 'Редактировать профиль',
      saveChanges: 'Сохранить изменения',
      cancel: 'Отмена',
      saving: 'Сохранение...',
      accountInfo: 'Информация об аккаунте',
      accountStatus: 'Статус аккаунта:',
      emailVerified: 'Email подтвержден:',
      memberSince: 'Участник с:',
      active: 'Активен',
      inactive: 'Неактивен',
      yes: 'Да',
      no: 'Нет',
    },
    telegramAccounts: {
      title: 'Telegram Аккаунты',
      subtitle: 'Подключите ваши Telegram аккаунты для мониторинга каналов и чатов',
      addAccount: '+ Добавить аккаунт',
      noAccountsTitle: 'Telegram аккаунты не подключены',
      noAccountsDesc: 'Подключите свой первый Telegram аккаунт, чтобы начать мониторинг каналов',
      addFirstAccount: 'Добавить первый аккаунт',
      status: 'Статус:',
      connected: 'Подключен:',
      lastActive: 'Последняя активность:',
      viewSources: 'Смотреть источники',
      disconnect: 'Отключить',

      // Modal
      addAccountModal: 'Добавить Telegram аккаунт',
      enterPhoneDesc: 'Введите ваш номер телефона для получения кода подтверждения',
      enterCodeDesc: 'Введите код подтверждения, отправленный в ваше приложение Telegram',
      phoneNumber: 'Номер телефона',
      phonePlaceholder: '+1234567890',
      verificationCode: 'Код подтверждения',
      codePlaceholder: '12345',
      cancel: 'Отмена',
      sendCode: 'Отправить код',
      verify: 'Подтвердить',
      codeSentTo: 'Код подтверждения отправлен на {{phone}}',

      // Validation & errors
      enterPhone: 'Пожалуйста, введите номер телефона',
      enterCode: 'Пожалуйста, введите код подтверждения',
      disconnectConfirm: 'Вы уверены, что хотите отключить этот Telegram аккаунт?',
      failedToLoad: 'Не удалось загрузить аккаунты',
      failedToSendCode: 'Не удалось отправить код',
      failedToVerify: 'Не удалось подтвердить код',
      failedToDelete: 'Не удалось удалить аккаунт',
    },
    sources: {
      title: 'Источники мониторинга',
      subtitle: 'Telegram каналы и группы, которые вы мониторите для поиска лидов',
      addSource: '+ Добавить источник',
      addModalTitle: 'Добавить источник мониторинга',
      addModalDesc: 'Выберите Telegram канал или группу для мониторинга',
      addSourceButton: 'Добавить источник',
      selectAccount: 'Выберите аккаунт Telegram',
      selectChannelOrGroup: 'Выберите канал или группу',
      noChannelsFound: 'Каналы не найдены',
      channel: 'Канал',
      group: 'Группа',
      members: 'участников',
      connectAccountFirst: 'Сначала подключите Telegram аккаунт',
      noSources: 'Нет источников',
      noSourcesDesc: 'Добавьте каналы и группы для начала мониторинга',
      addFirstSource: 'Добавить первый источник',
      unnamed: 'Без названия',
      subscribers: 'Подписчиков',
      type: 'Тип:',
      added: 'Добавлен:',
      pause: 'Пауза',
      activate: 'Активировать',
      remove: 'Удалить',
      active: 'Активен',
      paused: 'Приостановлен',
      confirmDelete: 'Вы уверены, что хотите удалить этот источник?',
      failedToLoad: 'Не удалось загрузить источники',
      failedToLoadChannels: 'Не удалось загрузить каналы',
      selectChannel: 'Пожалуйста, выберите канал',
      failedToAdd: 'Не удалось добавить источник',
      failedToUpdate: 'Не удалось обновить источник',
      failedToDelete: 'Не удалось удалить источник',
    },
    leads: {
      title: 'Лиды',
      subtitle: 'Сообщения, соответствующие вашим правилам мониторинга',
      status: 'Статус',
      allStatuses: 'Все статусы',
      rule: 'Правило',
      allRules: 'Все правила',
      source: 'Источник',
      allSources: 'Все источники',
      exportCSV: 'Экспорт в CSV',
      exporting: 'Экспорт...',
      noLeads: 'Лиды не найдены',
      noLeadsDesc: 'Лиды появятся здесь, когда сообщения будут соответствовать вашим правилам',
      tryAdjustingFilters: 'Попробуйте изменить фильтры',
      filters: 'Фильтры',
      resetFilters: 'Сбросить фильтры',
      score: 'Оценка',
      viewDetails: 'Подробнее',
      showing: 'Показано',
      previous: 'Предыдущая',
      next: 'Следующая',

      // Detail modal
      leadDetails: 'Детали лида',
      completeInformation: 'Полная информация об этом лиде',
      confidenceScore: 'Оценка уверенности',
      created: 'Создано',
      message: 'Сообщение',
      views: 'Просмотры',
      links: 'Ссылки',
      llmAnalysis: 'Анализ LLM',
      extractedInformation: 'Извлеченная информация',
      contacts: 'Контакты',
      keywords: 'Ключевые слова',
      budget: 'Бюджет',
      deadline: 'Срок',
      matchedRule: 'Совпавшее правило',
      openInTelegram: 'Открыть в Telegram',
      deleteConfirm: 'Вы уверены, что хотите удалить этот лид?',
      totalLeads: 'Всего лидов',
      foundLeads: 'Найдено',
    },
    rules: {
      title: 'Правила мониторинга',
      subtitle: 'Правила на основе LLM для поиска релевантных лидов в сообщениях Telegram',
      addRule: '+ Добавить правило',
      noRules: 'Правила еще не созданы',
      noRulesDesc: 'Создайте первое правило мониторинга, чтобы начать находить лиды',
      createFirstRule: 'Создать первое правило',
      editRule: 'Редактировать правило',
      addNewRule: 'Добавить новое правило',
      createRulesDesc: 'Создайте правила на основе LLM для автоматического поиска релевантных лидов',
      ruleFormDesc: 'Заполните детали для создания нового правила мониторинга',
      noDescription: 'Описание не предоставлено',

      // Form fields
      ruleName: 'Название правила',
      ruleNamePlaceholder: 'например, Вакансии Python разработчиков',
      description: 'Описание',
      descriptionOptional: 'Описание (опционально)',
      descriptionPlaceholder: 'Краткое описание того, что ищет это правило',
      llmPrompt: 'LLM Промпт',
      llmPromptPlaceholder: 'Опишите какие сообщения вы ищете. Будьте конкретны о критериях, ключевых словах, контексте и т.д.\n\nПример: "Найти сообщения, где кто-то ищет Python разработчика с опытом Django, упоминает бюджет выше $100k и нужно начать в течение 1-2 месяцев."',
      llmPromptHint: 'Этот промпт будет использован LLM для анализа сообщений',
      confidenceThreshold: 'Порог уверенности',
      confidenceThresholdHint: 'Минимальная оценка уверенности LLM для создания лида (выше = меньше, но более релевантных лидов)',
      applyToSources: 'Применить к источникам',
      applyToSourcesHint: 'Выберите конкретные источники или оставьте пустым для применения ко всем',
      noSourcesAvailable: 'Источники недоступны. Сначала добавьте Telegram каналы.',
      addChannelsFirst: 'Сначала добавьте Telegram каналы.',
      activeStartImmediately: 'Активно (начать мониторинг немедленно)',

      // Card labels
      threshold: 'Порог',
      sources: 'Источники',
      selectedSources: 'выбрано',
      sourcesSelected: 'Выбрано источников: {{count}}',
      allSources: 'Все источники',
      leadsFound: 'Найдено лидов',

      // Status badges
      active: 'Активно',
      paused: 'Приостановлено',

      // Actions
      edit: 'Редактировать',
      test: 'Тест',
      testRule: 'Тестировать правило',
      activate: 'Активировать',
      pause: 'Приостановить',
      delete: 'Удалить',

      // Test modal
      testRuleTitle: 'Тестирование правила',
      testRuleDesc: 'Протестируйте, как это правило будет анализировать пример сообщения',
      sampleMessage: 'Пример сообщения',
      sampleMessagePlaceholder: 'Вставьте сообщение для тестирования против этого правила...',
      match: 'Совпадение',
      yes: 'Да',
      no: 'Нет',
      confidence: 'Уверенность',
      wouldCreateLead: 'Создаст лид',
      llmReasoning: 'Обоснование LLM',
      extractedEntities: 'Извлеченные сущности',
      contacts: 'Контакты',
      keywords: 'Ключевые слова',
      budget: 'Бюджет',
      deadline: 'Срок',

      // Validation & errors
      enterRuleName: 'Пожалуйста, введите название правила',
      enterPrompt: 'Пожалуйста, введите промпт (минимум 10 символов)',
      enterTestMessage: 'Пожалуйста, введите сообщение для теста',
      confirmDelete: 'Вы уверены? Все связанные лиды также будут удалены.',
      deleteConfirm: 'Вы уверены? Все связанные лиды также будут удалены.',
      saveChanges: 'Сохранить изменения',
      createRule: 'Создать правило',
      failedToLoad: 'Не удалось загрузить правила',
      failedToSave: 'Не удалось сохранить правило',
      failedToDelete: 'Не удалось удалить правило',
      failedToUpdate: 'Не удалось обновить правило',
      failedToTest: 'Не удалось протестировать правило',
    },
    analytics: {
      title: 'Аналитика',
      subtitle: 'Подробная статистика и метрики вашей системы мониторинга',
      loadingAnalytics: 'Загрузка аналитики...',

      // Summary cards
      totalLeads: 'Всего лидов',
      last30Days: 'За последние 30 дней',
      messagesCollected: 'Собрано сообщений',
      conversion: 'Конверсия',
      messagesToLeads: 'Сообщения → Лиды',
      avgScore: 'Средний Score',
      leadQuality: 'Качество лидов',

      // Activity trends
      activityTrends: 'Тренды активности',
      period: 'Период',
      previous: 'Предыдущий',

      // Time series
      leadsOverTime: 'Создание лидов за период',

      // Conversion funnel
      conversionFunnel: 'Воронка конверсии',
      totalConversion: 'Общая конверсия',
      leads: 'лидов',
      conversionRate: 'конверсия',

      // Top performers
      topSource: 'Топ источник',
      mostLeads: 'Больше всего лидов',
      topRule: 'Топ правило',

      // Performance tables
      sourcePerformance: 'Производительность источников',
      topSources: 'Топ источников',
      source: 'Источник',
      messages: 'Сообщений',

      rulePerformance: 'Производительность правил',
      allRules: 'Все правила и их эффективность',
      rule: 'Правило',
      totalLeadsLabel: 'Всего лидов',
      last7Days: '7д',
      last30DaysLabel: '30д',
      status: 'Статус',
      active: 'Активно',
      inactive: 'Неактивно',
    },
    settings: {
      title: 'Настройки',
      subtitle: 'Управление уведомлениями и настройками аккаунта',

      // Notifications section
      notificationSettings: 'Настройки уведомлений',
      notificationSettingsDesc: 'Выберите, какие уведомления вы хотите получать',

      // Global toggles
      emailNotifications: 'Email уведомления',
      emailNotificationsDesc: 'Получать уведомления на email',
      inAppNotifications: 'In-app уведомления',
      inAppNotificationsDesc: 'Показывать уведомления в приложении (колокольчик в header)',

      // Event types
      eventTypes: 'Типы событий',
      newLeads: 'Новые лиды',
      newLeadsDesc: 'Уведомлять, когда система находит новый лид, соответствующий вашим правилам',
      leadStatusChange: 'Изменение статуса лида',
      leadStatusChangeDesc: 'Уведомлять, когда статус лида изменяется (new → in progress → processed)',
      leadAssignment: 'Назначение лида',
      leadAssignmentDesc: 'Уведомлять, когда лид назначается на вас',

      // Actions
      saveSettings: 'Сохранить настройки',
      saving: 'Сохранение...',

      // Messages
      loadingSettings: 'Загрузка настроек...',
      settingsSaved: 'Настройки сохранены успешно!',
      failedToLoad: 'Не удалось загрузить настройки',
      failedToSave: 'Не удалось сохранить настройки',
    },
    notifications: {
      title: 'Уведомления',
      markAllRead: 'Прочитать все',
      loading: 'Загрузка...',
      noNotifications: 'Нет уведомлений',
      markRead: 'Прочитать',
      viewAll: 'Все уведомления',
    },
    time: {
      justNow: 'только что',
      minutesAgo: '{{count}}м назад',
      hoursAgo: '{{count}}ч назад',
      daysAgo: '{{count}}д назад',
    },
    leadStatus: {
      new: 'Новый',
      in_progress: 'В работе',
      processed: 'Обработан',
      archived: 'Архив',
    },
    notificationType: {
      leadCreated: 'Новый лид',
      leadStatusChanged: 'Изменение статуса',
      leadAssigned: 'Назначение лида',
      ruleTriggered: 'Правило сработало',
      system: 'Системное',
    },
    breadcrumbs: {
      home: 'Главная',
      dashboard: 'Дашборд',
      telegramAccounts: 'Telegram Аккаунты',
      sources: 'Источники',
      rules: 'Правила',
      leads: 'Лиды',
      analytics: 'Аналитика',
      settings: 'Настройки',
      profile: 'Профиль',
    },
    charts: {
      noData: 'Нет данных для отображения',
    },
    common: {
      loading: 'Загрузка...',
      error: 'Ошибка',
      success: 'Успешно',
      save: 'Сохранить',
      cancel: 'Отмена',
      delete: 'Удалить',
      edit: 'Редактировать',
      close: 'Закрыть',
      back: 'Назад',
      yes: 'Да',
      no: 'Нет',
      active: 'Активно',
      inactive: 'Неактивно',
      confirm: 'Подтвердить',
      search: 'Поиск',
      filter: 'Фильтр',
      sort: 'Сортировка',
      showing: 'Показано',
      of: 'из',
      items: 'элементов',
      noDataAvailable: 'Нет доступных данных',
      somethingWentWrong: 'Что-то пошло не так',
      tryAgain: 'Попробовать снова',
      areYouSure: 'Вы уверены?',
    },
  },
};
