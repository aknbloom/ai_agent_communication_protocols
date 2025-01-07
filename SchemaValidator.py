// Schema validation
interface ValidationRules {
 required: string[];
 types: Record<string, string>;
 formats: Record<string, RegExp>;
}

class SchemaValidator {
 validateMessage(message: any, schema: ValidationRules): ValidationResult {
   // Check required fields
   const missingFields = checkRequiredFields(message, schema.required);
   
   // Type validation
   const typeErrors = validateTypes(message, schema.types);
   
   // Format validation
   const formatErrors = validateFormats(message, schema.formats);
   
   return new ValidationResult(missingFields, typeErrors, formatErrors);
 }
}

// Migration utilities 
class SchemaMigration {
 migrateData(oldVersion: string, newVersion: string, data: any): any {
   const migrations = this.getMigrationPath(oldVersion, newVersion);
   return migrations.reduce((acc, migration) => migration(acc), data);
 }
}
