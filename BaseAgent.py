// Abstract base Agent class that leverages context management
class BaseAgent {
    constructor(agentId, contextManager) {
        this.agentId = agentId;
        this.contextManager = contextManager;
        this.capabilities = new Set();
        this.currentContext = null;
    }

    async initializeContext(parentContextId = null) {
        this.currentContext = this.contextManager.createContext(
            this.agentId,
            parentContextId
        );
        return this.currentContext;
    }

    async addCapability(capability) {
        this.capabilities.add(capability);
        await this.updateContextState();
    }

    async updateContextState() {
        if (this.currentContext) {
            this.contextManager.adaptContext(this.agentId, {
                capabilities: Array.from(this.capabilities),
                agentType: this.constructor.name
            });
        }
    }
}
