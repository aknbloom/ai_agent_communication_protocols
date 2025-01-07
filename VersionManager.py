// Version management
interface VersionConfig {
 major: number;
 minor: number;
 patch: number;
 supportedVersions: string[];
}

// Semantic versioning implementation
class VersionManager {
 negotiateVersion(clientVersion: string, serverVersions: string[]): string {
   // Find highest compatible version
   return maxCompatibleVersion(clientVersion, serverVersions);
 }

 checkBackwardCompatibility(oldSchema: Schema, newSchema: Schema): boolean {
   // Verify no breaking changes
   return validateSchemaCompatibility(oldSchema, newSchema);
 }
}
