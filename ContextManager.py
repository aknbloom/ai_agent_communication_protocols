class ContextManager {
  constructor() {
    this.activeContexts = new Map();
    this.stateHistory = [];
    this.adaptationRules = new Map();
  }

  // Create new context with preservation of parent context
  createContext(taskId, parentContextId = null) {
    const parentContext = parentContextId ? 
      this.activeContexts.get(parentContextId) : null;

    const context = {
      taskId,
      parentContext: parentContextId,
      created: Date.now(),
      state: 'initialized',
      environment: this.captureEnvironment(),
      recoveryPoints: [],
      adaptationHistory: []
    };

    if (parentContext) {
      context.inheritedCapabilities = parentContext.capabilities;
      context.parentState = parentContext.state;
    }

    this.activeContexts.set(taskId, context);
    this.stateHistory.push({
      taskId,
      action: 'context_created',
      timestamp: Date.now()
    });

    return context;
  }

  // Add checkpoint for potential recovery
  addRecoveryPoint(taskId, state) {
    const context = this.activeContexts.get(taskId);
    if (!context) return null;

    const recoveryPoint = {
      timestamp: Date.now(),
      state: state,
      environmentSnapshot: this.captureEnvironment()
    };

    context.recoveryPoints.push(recoveryPoint);
    return recoveryPoint;
  }

  // Adapt context based on new conditions
  adaptContext(taskId, newConditions) {
    const context = this.activeContexts.get(taskId);
    if (!context) return null;

    const adaptation = {
      timestamp: Date.now(),
      previousState: context.state,
      conditions: newConditions
    };

    // Apply adaptation rules
    const applicableRules = this.findApplicableRules(newConditions);
    const adaptedState = this.applyAdaptationRules(context, applicableRules);

    context.state = adaptedState;
    context.adaptationHistory.push(adaptation);

    return adaptedState;
  }

  // Restore context from recovery point
  restoreFromRecoveryPoint(taskId, recoveryPointIndex) {
    const context = this.activeContexts.get(taskId);
    if (!context || !context.recoveryPoints[recoveryPointIndex]) {
      return null;
    }

    const recoveryPoint = context.recoveryPoints[recoveryPointIndex];
    context.state = recoveryPoint.state;
    context.environment = recoveryPoint.environmentSnapshot;

    this.stateHistory.push({
      taskId,
      action: 'context_restored',
      timestamp: Date.now(),
      recoveryPoint: recoveryPointIndex
    });

    return context;
  }

  // Capture current environment state
  captureEnvironment() {
    return {
      timestamp: Date.now(),
      resources: this.getCurrentResourceState(),
      activeAgents: this.getActiveAgents(),
      systemLoad: this.getSystemLoad()
    };
  }

  // Helper methods for environment capture
  getCurrentResourceState() {
    // Implementation for resource state capture
    return {
      memory: process.memoryUsage(),
      cpu: process.cpuUsage()
    };
  }

  getActiveAgents() {
    // Implementation to get current active agents
    return Array.from(this.activeContexts.keys());
  }

  getSystemLoad() {
    // Implementation for system load measurement
    return {
      contextCount: this.activeContexts.size,
      historyDepth: this.stateHistory.length
    };
  }

  // Find applicable adaptation rules based on conditions
  findApplicableRules(conditions) {
    const applicableRules = [];
    for (const [ruleId, rule] of this.adaptationRules) {
      if (this.checkRuleConditions(rule, conditions)) {
        applicableRules.push(rule);
      }
    }
    return applicableRules;
  }

  // Apply adaptation rules to context
  applyAdaptationRules(context, rules) {
    let currentState = context.state;
    for (const rule of rules) {
      currentState = this.applyRule(currentState, rule);
    }
    return currentState;
  }
}

// Example usage:
const contextManager = new ContextManager();

// Create main task context
const mainContext = contextManager.createContext('task-123');

// Create subtask with parent context
const subtaskContext = contextManager.createContext('subtask-456', 'task-123');

// Add recovery point before risky operation
contextManager.addRecoveryPoint('subtask-456', {
  operation: 'data_processing',
  progress: 0.5
});

// Adapt context based on new conditions
contextManager.adaptContext('subtask-456', {
  resourceConstraints: true,
  errorRate: 0.15
});

// Restore from recovery point if needed
contextManager.restoreFromRecoveryPoint('subtask-456', 0);
