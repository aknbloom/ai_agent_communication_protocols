// Specialized Research Agent - Focuses on information gathering and analysis
class ResearchAgent extends BaseAgent {
    constructor(agentId, contextManager) {
        super(agentId, contextManager);
        this.searchDepth = 0;
        this.confidenceThreshold = 0.8;
    }

    async initializeSpecialization() {
        await this.addCapability('deep_search');
        await this.addCapability('fact_verification');
        await this.addCapability('source_citation');
    }

    async adaptSearchStrategy(complexity) {
        const adaptedContext = this.contextManager.adaptContext(this.agentId, {
            searchDepth: this.calculateSearchDepth(complexity),
            verificationLevel: this.determineVerificationLevel(complexity)
        });
        
        this.searchDepth = adaptedContext.searchDepth;
        return adaptedContext;
    }

    calculateSearchDepth(complexity) {
        return Math.min(complexity * 2, 10); // Max depth of 10
    }

    determineVerificationLevel(complexity) {
        return complexity > 5 ? 'rigorous' : 'standard';
    }
}
