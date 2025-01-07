message Context {
  // Basic context
  string conversation_id = 1;
  int64 timestamp = 2;
  repeated string previous_messages = 3;

  // Enhanced context
  StateTracking state = 4;
  ExecutionContext execution = 5;
  MemoryContext memory = 6;
}

message StateTracking {
  map<string, any> agent_states = 1;
  repeated StateTransition transitions = 2;
}

message ExecutionContext {
  repeated TaskDependency dependencies = 1;
  map<string, Priority> priorities = 2;
}

message MemoryContext {
  repeated ConversationMemory short_term = 1;
  map<string, bytes> long_term = 2;
}
