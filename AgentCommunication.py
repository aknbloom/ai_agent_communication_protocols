message AgentCommunication {
  string message_id = 1;
  string source_agent = 2;
  string target_agent = 3;
  MessageType type = 4;
  bytes payload = 5;
  map<string, string> metadata = 6;
  int32 version = 7;
  Context context = 8;
}

message Context {
  string conversation_id = 1;
  int64 timestamp = 2;
  repeated string previous_messages = 3;
  map<string, string> custom_attributes = 4;
}
