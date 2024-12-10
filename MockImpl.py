// Example usage:
const contextManager = new ContextManager();

// Initialize specialized agents
const researcher = new ResearchAgent('researcher-1', contextManager);
await researcher.initializeSpecialization();

const executor = new TaskExecutionAgent('executor-1', contextManager);
await executor.initializeSpecialization();

const learner = new LearningAgent('learner-1', contextManager);
await learner.initializeSpecialization();

// Collaborative task execution
const researchContext = await researcher.initializeContext();
const executionContext = await executor.initializeContext(researchContext.taskId);
const learningContext = await learner.initializeContext(executionContext.taskId);
