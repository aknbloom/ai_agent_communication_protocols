// Specialized Learning Agent - Focuses on improving and adapting
class LearningAgent extends BaseAgent {
    constructor(agentId, contextManager) {
        super(agentId, contextManager);
        this.learningRate = 0.1;
        this.knowledgeBase = new Map();
    }

    async initializeSpecialization() {
        await this.addCapability('pattern_recognition');
        await this.addCapability('knowledge_integration');
        await this.addCapability('adaptive_learning');
    }

    async adaptLearningStrategy(performanceMetrics) {
        const adaptedContext = this.contextManager.adaptContext(this.agentId, {
            learningRate: this.calculateNewLearningRate(performanceMetrics),
            focusAreas: this.identifyFocusAreas(performanceMetrics)
        });

        this.learningRate = adaptedContext.learningRate;
        return adaptedContext;
    }

    calculateNewLearningRate(metrics) {
        const performance = metrics.successRate || 0.5;
        return Math.max(0.01, Math.min(0.5, this.learningRate * (1 + (performance - 0.5))));
    }

    identifyFocusAreas(metrics) {
        return Object.entries(metrics)
            .filter(([_, value]) => value < 0.7)
            .map(([area]) => area);
    }
}
