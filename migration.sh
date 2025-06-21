#!/usr/bin/env python3
"""
Migration script to update existing template and style profile files
to the new unified structure format.
"""

import os
import yaml
import shutil
from datetime import datetime
from pathlib import Path

def backup_files(source_dir, backup_dir):
    """Create backup of existing files"""
    if os.path.exists(source_dir):
        backup_path = os.path.join(backup_dir, f"{os.path.basename(source_dir)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        shutil.copytree(source_dir, backup_path)
        print(f"✅ Backed up {source_dir} to {backup_path}")
        return backup_path
    return None

def migrate_template_file(file_path):
    """Migrate a single template file to unified structure"""
    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        if not data:
            print(f"⚠️ Empty file: {file_path}")
            return False
        
        # Get filename without extension for ID
        filename = os.path.basename(file_path)
        template_id = filename.replace('.yaml', '')
        
        # Create new unified structure
        unified_data = {
            'id': data.get('id', template_id),
            'name': data.get('name', template_id.replace('_', ' ').title()),
            'description': data.get('description', ''),
            'category': data.get('category', 'general'),
            'slug': data.get('slug', template_id.replace('_', '-')),
        }
        
        # Add metadata
        unified_data['metadata'] = {
            'version': data.get('version', '1.0.0'),
            'created_by': 'migration_script',
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'migrated_from': 'legacy_format'
        }
        unified_data['metadata'].update(data.get('metadata', {}))
        
        # Handle defaults section
        defaults = {}
        for key in ['platform', 'title', 'audience', 'tone', 'length', 'code', 'tags']:
            if key in data:
                defaults[key] = data[key]
        
        if defaults:
            unified_data['defaults'] = defaults
        
        # Handle system_prompt
        if 'system_prompt' in data:
            unified_data['system_prompt'] = data['system_prompt']
        
        # Handle structure
        if 'structure' in data:
            unified_data['structure'] = data['structure']
        
        # Handle research
        if 'research' in data:
            unified_data['research'] = data['research']
        
        # Handle parameters - normalize to list format
        if 'parameters' in data:
            parameters_data = data['parameters']
            
            if isinstance(parameters_data, dict):
                # Convert dict to list format
                parameters_list = []
                for param_name, param_config in parameters_data.items():
                    if isinstance(param_config, dict):
                        param_item = {'name': param_name}
                        param_item.update(param_config)
                        parameters_list.append(param_item)
                    else:
                        # Simple parameter
                        parameters_list.append({
                            'name': param_name,
                            'label': param_name.replace('_', ' ').title(),
                            'type': 'string',
                            'required': False
                        })
                unified_data['parameters'] = parameters_list
            
            elif isinstance(parameters_data, list):
                # Already in list format, ensure all have required fields
                normalized_params = []
                for param in parameters_data:
                    if isinstance(param, dict) and 'name' in param:
                        normalized_param = {
                            'name': param['name'],
                            'label': param.get('label', param['name'].replace('_', ' ').title()),
                            'type': param.get('type', 'string'),
                            'required': param.get('required', False)
                        }
                        # Add optional fields if present
                        for optional_field in ['description', 'placeholder', 'default', 'options']:
                            if optional_field in param:
                                normalized_param[optional_field] = param[optional_field]
                        
                        normalized_params.append(normalized_param)
                    elif isinstance(param, str):
                        normalized_params.append({
                            'name': param,
                            'label': param.replace('_', ' ').title(),
                            'type': 'string',
                            'required': False
                        })
                
                unified_data['parameters'] = normalized_params
        
        # Write updated file
        with open(file_path, 'w') as f:
            yaml.dump(unified_data, f, default_flow_style=False, allow_unicode=True)
        
        print(f"✅ Migrated template: {filename}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to migrate {file_path}: {e}")
        return False

def migrate_style_profile_file(file_path):
    """Migrate a single style profile file to unified structure"""
    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        if not data:
            print(f"⚠️ Empty file: {file_path}")
            return False
        
        # Get filename without extension for ID
        filename = os.path.basename(file_path)
        profile_id = filename.replace('.yaml', '')
        
        # Create new unified structure
        unified_data = {
            'id': data.get('id', profile_id),
            'name': data.get('name', profile_id.replace('_', ' ').title()),
            'description': data.get('description', ''),
            'category': data.get('category', 'general'),
            'platform': data.get('platform'),
            'tone': data.get('tone'),
            'voice': data.get('voice'),
            'structure': data.get('structure'),
            'audience': data.get('audience'),
        }
        
        # Add system_prompt
        if 'system_prompt' in data:
            unified_data['system_prompt'] = data['system_prompt']
        
        # Add length_limit
        if 'length_limit' in data:
            unified_data['length_limit'] = data['length_limit']
        elif any(key in data for key in ['words', 'min', 'max']):
            # Convert old format
            length_limit = {}
            if 'words' in data:
                length_limit['words'] = data['words']
            if 'min' in data:
                length_limit['min'] = data['min']
            if 'max' in data:
                length_limit['max'] = data['max']
            unified_data['length_limit'] = length_limit
        
        # Add settings section
        settings = {}
        setting_keys = [
            'use_analogies', 'avoid_jargon', 'include_examples', 
            'conversational_tone', 'encourage_questions', 'reading_level'
        ]
        for key in setting_keys:
            if key in data:
                settings[key] = data[key]
        
        if settings:
            unified_data['settings'] = settings
        
        # Add formatting section
        formatting = {}
        formatting_keys = [
            'use_headers', 'use_bullet_points', 'use_callouts', 'code_blocks'
        ]
        for key in formatting_keys:
            if key in data:
                formatting[key] = data[key]
        
        if formatting:
            unified_data['formatting'] = formatting
        
        # Add metadata
        unified_data['metadata'] = {
            'version': data.get('version', '1.0.0'),
            'created_by': 'migration_script',
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'migrated_from': 'legacy_format'
        }
        if 'use_cases' in data:
            unified_data['metadata']['use_cases'] = data['use_cases']
        unified_data['metadata'].update(data.get('metadata', {}))
        
        # Remove None values
        unified_data = {k: v for k, v in unified_data.items() if v is not None}
        
        # Write updated file
        with open(file_path, 'w') as f:
            yaml.dump(unified_data, f, default_flow_style=False, allow_unicode=True)
        
        print(f"✅ Migrated style profile: {filename}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to migrate {file_path}: {e}")
        return False

def migrate_directory(directory, file_type):
    """Migrate all files in a directory"""
    if not os.path.exists(directory):
        print(f"⚠️ Directory not found: {directory}")
        return 0, 0
    
    migrated = 0
    failed = 0
    
    for filename in os.listdir(directory):
        if filename.endswith('.yaml'):
            file_path = os.path.join(directory, filename)
            
            if file_type == 'template':
                success = migrate_template_file(file_path)
            elif file_type == 'style_profile':
                success = migrate_style_profile_file(file_path)
            else:
                continue
            
            if success:
                migrated += 1
            else:
                failed += 1
    
    return migrated, failed

def main():
    """Main migration function"""
    print("🔄 Starting Migration to Unified File Structures")
    print("=" * 60)
    
    # Create backup directory
    backup_dir = f"backups/{datetime.now().strftime('%Y%m%d_%H%M%S')}_pre_migration"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Backup existing files
    template_dirs = [
        "data/content_templates",
        "frontend/content-templates"
    ]
    
    style_dirs = [
        "data/style_profiles", 
        "style_profiles",
        "frontend/style-profiles"
    ]
    
    print("📦 Creating backups...")
    for template_dir in template_dirs:
        backup_files(template_dir, backup_dir)
    
    for style_dir in style_dirs:
        backup_files(style_dir, backup_dir)
    
    # Migrate templates
    print("\n📄 Migrating content templates...")
    total_templates_migrated = 0
    total_templates_failed = 0
    
    for template_dir in template_dirs:
        if os.path.exists(template_dir):
            print(f"\n📁 Processing {template_dir}")
            migrated, failed = migrate_directory(template_dir, 'template')
            total_templates_migrated += migrated
            total_templates_failed += failed
            print(f"   ✅ {migrated} migrated, ❌ {failed} failed")
    
    # Migrate style profiles
    print("\n🎨 Migrating style profiles...")
    total_profiles_migrated = 0
    total_profiles_failed = 0
    
    for style_dir in style_dirs:
        if os.path.exists(style_dir):
            print(f"\n📁 Processing {style_dir}")
            migrated, failed = migrate_directory(style_dir, 'style_profile')
            total_profiles_migrated += migrated
            total_profiles_failed += failed
            print(f"   ✅ {migrated} migrated, ❌ {failed} failed")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Migration Summary")
    print("=" * 60)
    print(f"📄 Templates: {total_templates_migrated} migrated, {total_templates_failed} failed")
    print(f"🎨 Style Profiles: {total_profiles_migrated} migrated, {total_profiles_failed} failed")
    print(f"📦 Backups saved to: {backup_dir}")
    
    if total_templates_failed == 0 and total_profiles_failed == 0:
        print("\n🎉 Migration completed successfully!")
    else:
        print(f"\n⚠️ Migration completed with {total_templates_failed + total_profiles_failed} failures")
        print("Check the error messages above and the backup files if needed")
    
    print("\n💡 Next steps:")
    print("1. Update your server.py with the new loader functions")
    print("2. Restart your FastAPI server")
    print("3. Test the /debug/file-structures endpoint")
    print("4. Test content generation")

if __name__ == "__main__":
    main()