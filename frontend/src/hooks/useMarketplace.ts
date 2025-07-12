/**
 * Hook for managing marketplace data and user module subscriptions
 * Provides marketplace functionality with mock data for development
 */

import { useState, useEffect, useMemo } from 'react';
import type { 
    Module, 
    UserModuleSubscription, 
    MarketplaceSearchParams, 
    MarketplaceStats,
    ModuleExecutionResult,
    ModuleAuthor
} from '@/types/marketplace';

// Mock authors
const mockAuthors: ModuleAuthor[] = [
    {
        id: 'author-1',
        name: 'Dr. Sarah Chen',
        email: 'sarah.chen@academitech.com',
        organization: 'AcademiTech Solutions',
        avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b47c?w=150',
        verified: true,
        reputation: 4.8
    },
    {
        id: 'author-2',
        name: 'Prof. Michael Rodriguez',
        email: 'm.rodriguez@university.edu',
        organization: 'University Research Lab',
        avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150',
        verified: true,
        reputation: 4.9
    },
    {
        id: 'author-3',
        name: 'ResearchBot Team',
        email: 'team@researchbot.ai',
        organization: 'ResearchBot AI',
        avatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150',
        verified: true,
        reputation: 4.7
    }
];

// Mock modules data
const generateMockModules = (): Module[] => [
    {
        id: 'citation-validator-pro',
        name: 'citation-validator-pro',
        displayName: 'Citation Validator Pro',
        description: 'Advanced citation validation and verification system',
        longDescription: 'A comprehensive module that automatically validates citations in scientific papers. It checks for trustworthiness, currency, correct interpretation, and proper formatting according to various academic standards.',
        icon: 'BookCheck',
        category: 'citation',
        tags: ['citation', 'validation', 'accuracy', 'formatting'],
        author: mockAuthors[0],
        currentVersion: '2.1.0',
        versions: [
            {
                version: '2.1.0',
                releaseDate: '2025-07-01',
                changelog: 'Added support for IEEE citation format, improved accuracy by 15%',
                downloadUrl: '/modules/citation-validator-pro-2.1.0.zip',
                size: 25600000,
                requirements: ['internet-connection'],
                isCompatible: true
            }
        ],
        license: {
            type: 'freemium',
            price: 29.99,
            currency: 'USD',
            billingCycle: 'monthly',
            trialPeriod: 14,
            features: {
                free: ['Basic citation validation', 'APA format support', 'Up to 10 citations per document'],
                premium: ['Advanced validation algorithms', 'All citation formats', 'Unlimited citations', 'Batch processing', 'API access']
            }
        },
        downloads: 15420,
        rating: {
            average: 4.7,
            count: 342
        },
        reviews: [],
        capabilities: {
            analysisTypes: ['citation-validation'],
            supportedFormats: ['pdf', 'docx', 'tex'],
            supportedLanguages: ['en', 'es', 'fr', 'de'],
            requiresInternet: true,
            estimatedProcessingTime: 45,
            maxFileSize: 50
        },
        configuration: {
            citationFormat: {
                type: 'select',
                label: 'Citation Format',
                description: 'Select the citation format to validate against',
                required: true,
                default: 'apa',
                options: [
                    { value: 'apa', label: 'APA 7th Edition' },
                    { value: 'mla', label: 'MLA 9th Edition' },
                    { value: 'chicago', label: 'Chicago 17th Edition' },
                    { value: 'ieee', label: 'IEEE' }
                ]
            },
            strictMode: {
                type: 'boolean',
                label: 'Strict Validation',
                description: 'Enable strict validation mode for enhanced accuracy',
                required: false,
                default: true
            },
            checkTrustworthiness: {
                type: 'boolean',
                label: 'Check Source Trustworthiness',
                description: 'Verify the reliability and reputation of cited sources',
                required: false,
                default: true
            }
        },
        screenshots: [
            'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800',
            'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800'
        ],
        documentation: 'Complete documentation available at /docs/citation-validator-pro',
        demoUrl: '/demo/citation-validator-pro',
        status: 'active',
        featured: true,
        verified: true,
        createdAt: '2024-12-15T10:00:00Z',
        updatedAt: '2025-07-01T14:30:00Z',
        publishedAt: '2025-01-15T09:00:00Z'
    },
    {
        id: 'plagiarism-detector',
        name: 'plagiarism-detector',
        displayName: 'PlagiarismShield',
        description: 'AI-powered plagiarism detection and similarity analysis',
        longDescription: 'Advanced plagiarism detection system using machine learning to identify potential plagiarism, text similarity, and proper attribution issues in academic documents.',
        icon: 'Shield',
        category: 'analysis',
        tags: ['plagiarism', 'detection', 'similarity', 'integrity'],
        author: mockAuthors[2],
        currentVersion: '1.5.2',
        versions: [
            {
                version: '1.5.2',
                releaseDate: '2025-06-20',
                changelog: 'Improved AI model accuracy, added support for mathematical formulas',
                downloadUrl: '/modules/plagiarism-detector-1.5.2.zip',
                size: 89600000,
                requirements: ['gpu-acceleration-optional'],
                isCompatible: true
            }
        ],
        license: {
            type: 'subscription',
            price: 49.99,
            currency: 'USD',
            billingCycle: 'monthly',
            trialPeriod: 7,
            features: {
                free: [],
                premium: ['Full plagiarism detection', 'AI similarity analysis', 'Citation recommendation', 'Batch processing', 'Detailed reports']
            }
        },
        downloads: 8930,
        rating: {
            average: 4.5,
            count: 187
        },
        reviews: [],
        capabilities: {
            analysisTypes: ['plagiarism-check', 'bias-detection'],
            supportedFormats: ['pdf', 'docx', 'txt', 'md'],
            supportedLanguages: ['en', 'es', 'fr', 'de', 'zh'],
            requiresInternet: true,
            estimatedProcessingTime: 120,
            maxFileSize: 100
        },
        configuration: {
            sensitivityLevel: {
                type: 'select',
                label: 'Detection Sensitivity',
                description: 'Set the sensitivity level for plagiarism detection',
                required: true,
                default: 'medium',
                options: [
                    { value: 'low', label: 'Low - Only exact matches' },
                    { value: 'medium', label: 'Medium - Similar phrases' },
                    { value: 'high', label: 'High - Paraphrased content' }
                ]
            },
            excludeQuotes: {
                type: 'boolean',
                label: 'Exclude Quoted Text',
                description: 'Ignore properly quoted text in plagiarism analysis',
                required: false,
                default: true
            }
        },
        screenshots: [
            'https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=800',
            'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800'
        ],
        documentation: 'Documentation available at /docs/plagiarism-detector',
        status: 'active',
        featured: false,
        verified: true,
        createdAt: '2024-11-20T10:00:00Z',
        updatedAt: '2025-06-20T16:45:00Z',
        publishedAt: '2025-02-01T11:00:00Z'
    },
    {
        id: 'quality-assessor',
        name: 'quality-assessor',
        displayName: 'Academic Quality Assessor',
        description: 'Comprehensive quality assessment for academic papers',
        longDescription: 'Evaluates the overall quality of academic papers including methodology, structure, argumentation, evidence quality, and adherence to academic standards.',
        icon: 'Award',
        category: 'analysis',
        tags: ['quality', 'assessment', 'methodology', 'structure'],
        author: mockAuthors[1],
        currentVersion: '3.0.1',
        versions: [
            {
                version: '3.0.1',
                releaseDate: '2025-07-05',
                changelog: 'Major update with new quality metrics and improved scoring system',
                downloadUrl: '/modules/quality-assessor-3.0.1.zip',
                size: 45200000,
                requirements: [],
                isCompatible: true
            }
        ],
        license: {
            type: 'free',
            features: {
                free: ['Basic quality assessment', 'Structure analysis', 'Methodology review', 'Detailed reports']
            }
        },
        downloads: 23450,
        rating: {
            average: 4.8,
            count: 521
        },
        reviews: [],
        capabilities: {
            analysisTypes: ['quality-assessment', 'methodology-review'],
            supportedFormats: ['pdf', 'docx', 'tex', 'md'],
            supportedLanguages: ['en', 'es', 'fr', 'de', 'it', 'pt'],
            requiresInternet: false,
            estimatedProcessingTime: 90,
            maxFileSize: 75
        },
        configuration: {
            assessmentDepth: {
                type: 'select',
                label: 'Assessment Depth',
                description: 'Choose the depth of quality assessment',
                required: true,
                default: 'comprehensive',
                options: [
                    { value: 'basic', label: 'Basic - Structure and formatting' },
                    { value: 'standard', label: 'Standard - Includes methodology' },
                    { value: 'comprehensive', label: 'Comprehensive - Full analysis' }
                ]
            },
            includeLanguageAnalysis: {
                type: 'boolean',
                label: 'Include Language Analysis',
                description: 'Analyze writing quality and clarity',
                required: false,
                default: true
            }
        },
        screenshots: [
            'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=800'
        ],
        documentation: 'Documentation available at /docs/quality-assessor',
        status: 'active',
        featured: true,
        verified: true,
        createdAt: '2024-10-10T10:00:00Z',
        updatedAt: '2025-07-05T12:15:00Z',
        publishedAt: '2024-12-01T08:00:00Z'
    }
];

export function useMarketplace() {
    const [modules, setModules] = useState<Module[]>([]);
    const [userSubscriptions, setUserSubscriptions] = useState<UserModuleSubscription[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchParams, setSearchParams] = useState<MarketplaceSearchParams>({
        sortBy: 'popularity',
        sortOrder: 'desc',
        page: 1,
        limit: 12
    });

    // Initialize mock data
    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            
            // Simulate API delay
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            const mockModules = generateMockModules();
            setModules(mockModules);
            
            // Mock user subscriptions (user has subscribed to first two modules)
            setUserSubscriptions([
                {
                    moduleId: 'citation-validator-pro',
                    module: mockModules[0],
                    subscribedAt: '2025-06-01T10:00:00Z',
                    licenseType: 'premium',
                    expiresAt: '2025-08-01T10:00:00Z',
                    status: 'active',
                    configuration: {
                        citationFormat: 'apa',
                        strictMode: true,
                        checkTrustworthiness: true
                    },
                    usageStats: {
                        totalRuns: 45,
                        lastUsed: '2025-07-10T14:30:00Z',
                        averageProcessingTime: 42
                    }
                },
                {
                    moduleId: 'quality-assessor',
                    module: mockModules[2],
                    subscribedAt: '2025-05-15T09:00:00Z',
                    licenseType: 'free',
                    status: 'active',
                    configuration: {
                        assessmentDepth: 'comprehensive',
                        includeLanguageAnalysis: true
                    },
                    usageStats: {
                        totalRuns: 23,
                        lastUsed: '2025-07-08T11:20:00Z',
                        averageProcessingTime: 87
                    }
                }
            ]);
            
            setLoading(false);
        };

        loadData();
    }, []);

    // Filter and search modules
    const filteredModules = useMemo(() => {
        let filtered = [...modules];
        
        // Apply search query
        if (searchParams.query) {
            const query = searchParams.query.toLowerCase();
            filtered = filtered.filter(module =>
                module.displayName.toLowerCase().includes(query) ||
                module.description.toLowerCase().includes(query) ||
                module.tags.some(tag => tag.toLowerCase().includes(query))
            );
        }
        
        // Apply filters
        if (searchParams.filters) {
            const { filters } = searchParams;
            
            if (filters.category?.length) {
                filtered = filtered.filter(module => filters.category!.includes(module.category));
            }
            
            if (filters.licenseType?.length) {
                filtered = filtered.filter(module => filters.licenseType!.includes(module.license.type));
            }
            
            if (filters.rating) {
                filtered = filtered.filter(module => module.rating.average >= filters.rating!);
            }
            
            if (filters.verified !== undefined) {
                filtered = filtered.filter(module => module.verified === filters.verified);
            }
            
            if (filters.featured !== undefined) {
                filtered = filtered.filter(module => module.featured === filters.featured);
            }
        }
        
        // Apply sorting
        filtered.sort((a, b) => {
            const direction = searchParams.sortOrder === 'desc' ? -1 : 1;
            
            switch (searchParams.sortBy) {
                case 'popularity':
                    return direction * (a.downloads - b.downloads);
                case 'rating':
                    return direction * (a.rating.average - b.rating.average);
                case 'newest':
                    return direction * (new Date(a.publishedAt).getTime() - new Date(b.publishedAt).getTime());
                case 'name':
                    return direction * a.displayName.localeCompare(b.displayName);
                case 'price':
                    const aPrice = a.license.price || 0;
                    const bPrice = b.license.price || 0;
                    return direction * (aPrice - bPrice);
                default:
                    return 0;
            }
        });
        
        return filtered;
    }, [modules, searchParams]);

    // Pagination
    const paginatedModules = useMemo(() => {
        const start = ((searchParams.page || 1) - 1) * (searchParams.limit || 12);
        const end = start + (searchParams.limit || 12);
        return filteredModules.slice(start, end);
    }, [filteredModules, searchParams.page, searchParams.limit]);

    const marketplaceStats: MarketplaceStats = useMemo(() => ({
        totalModules: modules.length,
        totalDownloads: modules.reduce((sum, module) => sum + module.downloads, 0),
        topCategories: [
            { category: 'citation', count: modules.filter(m => m.category === 'citation').length },
            { category: 'analysis', count: modules.filter(m => m.category === 'analysis').length },
            { category: 'formatting', count: modules.filter(m => m.category === 'formatting').length }
        ],
        featuredModules: modules.filter(m => m.featured),
        recentlyUpdated: modules.slice().sort((a, b) => 
            new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
        ).slice(0, 5)
    }), [modules]);

    const subscribeToModule = async (moduleId: string, licenseType: 'free' | 'premium') => {
        const module = modules.find(m => m.id === moduleId);
        if (!module) return;

        const subscription: UserModuleSubscription = {
            moduleId,
            module,
            subscribedAt: new Date().toISOString(),
            licenseType,
            expiresAt: licenseType === 'premium' && module.license.billingCycle === 'monthly' 
                ? new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString() 
                : undefined,
            status: 'active',
            configuration: {},
            usageStats: {
                totalRuns: 0,
                lastUsed: new Date().toISOString(),
                averageProcessingTime: 0
            }
        };

        setUserSubscriptions(prev => [...prev, subscription]);
    };

    const unsubscribeFromModule = async (moduleId: string) => {
        setUserSubscriptions(prev => prev.filter(sub => sub.moduleId !== moduleId));
    };

    const updateModuleConfiguration = async (moduleId: string, configuration: Record<string, any>) => {
        setUserSubscriptions(prev => prev.map(sub => 
            sub.moduleId === moduleId 
                ? { ...sub, configuration }
                : sub
        ));
    };

    const isModuleSubscribed = (moduleId: string) => {
        return userSubscriptions.some(sub => sub.moduleId === moduleId && sub.status === 'active');
    };

    const getUserSubscription = (moduleId: string) => {
        return userSubscriptions.find(sub => sub.moduleId === moduleId && sub.status === 'active');
    };

    return {
        // Data
        modules: paginatedModules,
        allModules: modules,
        userSubscriptions,
        marketplaceStats,
        loading,
        
        // Search and filters
        searchParams,
        setSearchParams,
        filteredModules,
        totalPages: Math.ceil(filteredModules.length / (searchParams.limit || 12)),
        
        // Actions
        subscribeToModule,
        unsubscribeFromModule,
        updateModuleConfiguration,
        isModuleSubscribed,
        getUserSubscription
    };
}
