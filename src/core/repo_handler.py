import os
import zipfile
import re
import requests
import base64
import time
from github import Github
from typing import Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class RepoHandler:
    def __init__(self, github_token: str = None):
        # Get GitHub token from environment if not provided
        if not github_token:
            github_token = os.getenv("GITHUB_TOKEN")
        
        # Only use token if it's not a placeholder
        if github_token and github_token != "your_github_token_here":
            self.github = Github(github_token)
            self.github_token = github_token
            print(f"Using authenticated GitHub API with token: {github_token[:10]}...")
        else:
            # Use unauthenticated access for public repositories
            self.github = Github()
            self.github_token = None
            print("Using unauthenticated GitHub API (rate limited)")
    
    def parse_github_url(self, url: str) -> tuple:
        """Parse GitHub URL to extract owner and repo name"""
        # Handle different GitHub URL formats
        patterns = [
            r'github\.com/([^/]+)/([^/]+?)(?:\.git)?(?:/.*)?$',
            r'github\.com/([^/]+)/([^/]+?)/?$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                owner, repo = match.groups()
                return owner, repo
        
        # If URL doesn't match patterns, try to extract from the end
        if 'github.com' in url:
            parts = url.replace('https://', '').replace('http://', '').split('/')
            if len(parts) >= 3:
                return parts[1], parts[2].replace('.git', '')
        
        raise ValueError(f"Could not parse GitHub URL: {url}")
    
    def fetch_github_repo(self, repo_url: str) -> Dict:
        """Fetch GitHub repository (public or private)"""
        try:
            owner, repo_name = self.parse_github_url(repo_url)
            repo_full_name = f"{owner}/{repo_name}"
            
            print(f"Fetching repository: {repo_full_name}")
            repo = self.github.get_repo(repo_full_name)
            contents = repo.get_contents("")
            
            return self._process_contents(contents, repo)
        except Exception as e:
            if "403" in str(e) and "rate limit" in str(e).lower():
                print("GitHub API rate limited, using fallback method...")
                return self.fetch_github_repo_fallback(repo_url)
            else:
                print(f"Error fetching GitHub repo: {e}")
                raise ValueError(f"Could not fetch repository: {str(e)}")
    
    def process_repo_zip(self, zip_path: str) -> Dict:
        """Process uploaded repository zip file"""
        import os
        import shutil
        
        # Clean up any existing temp directory
        temp_dir = './temp_repo'
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        print(f"Extracting ZIP file: {zip_path}")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Check if extraction created a nested directory structure
        # Often GitHub downloads create a folder like "repo-name-main/"
        extracted_items = os.listdir(temp_dir)
        print(f"Extracted items: {extracted_items}")
        
        # If there's only one directory and it looks like a root folder, use that
        if len(extracted_items) == 1 and os.path.isdir(os.path.join(temp_dir, extracted_items[0])):
            actual_repo_path = os.path.join(temp_dir, extracted_items[0])
            print(f"Using nested directory: {actual_repo_path}")
        else:
            actual_repo_path = temp_dir
            print(f"Using root directory: {actual_repo_path}")
        
        # Analyze the structure
        structure = self._analyze_structure(actual_repo_path)
        print(f"Found {len(structure)} files after analysis")
        
        # Print first few files for debugging
        if structure:
            print("Sample files found:")
            for i, (file_path, file_info) in enumerate(list(structure.items())[:5]):
                print(f"  {file_path} ({file_info.get('type', 'unknown')})")
        else:
            print("No files found! This might indicate a filtering issue.")
            # List all files in directory for debugging
            print("All files in directory:")
            for root, dirs, files in os.walk(actual_repo_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, actual_repo_path)
                    print(f"  {relative_path}")
        
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        return structure
    
    def _analyze_structure(self, path: str) -> Dict:
        """Analyze repository structure and extract metadata"""
        structure = {}
        
        # Define comprehensive file extensions to include
        code_extensions = (
            '.py', '.js', '.ts', '.jsx', '.tsx', '.vue', '.svelte',
            '.java', '.kotlin', '.scala', '.groovy',
            '.cpp', '.c', '.h', '.hpp', '.cc', '.cxx',
            '.cs', '.fs', '.vb',
            '.go', '.rs', '.swift', '.dart',
            '.php', '.rb', '.perl', '.pl',
            '.html', '.htm', '.xml', '.xhtml',
            '.css', '.scss', '.sass', '.less', '.stylus',
            '.sql', '.graphql', '.gql',
            '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd'
        )
        config_extensions = (
            '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.config',
            '.env', '.envrc', '.env.example', '.env.local', '.env.production',
            '.properties', '.settings', '.plist'
        )
        doc_extensions = (
            '.md', '.txt', '.rst', '.adoc', '.asciidoc', '.org', '.tex'
        )
        web_extensions = ('.html', '.css', '.scss', '.sass', '.less')
        data_extensions = ('.sql', '.xml', '.csv')
        build_extensions = (
            '.dockerfile', '.docker-compose.yml', '.docker-compose.yaml',
            '.gradle', '.maven', '.pom.xml', '.build.gradle', '.build.gradle.kts',
            '.cmake', '.cmakelist.txt', '.makefile', '.mk',
            '.webpack.config.js', '.rollup.config.js', '.vite.config.js',
            '.babel.config.js', '.eslint.config.js', '.prettier.config.js'
        )
        
        # Important files to always include (case-insensitive)
        important_files = {
            'readme.md', 'readme.txt', 'readme.rst', 'readme',
            'package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
            'requirements.txt', 'pyproject.toml', 'setup.py', 'pipfile', 'pipfile.lock',
            'cargo.toml', 'cargo.lock', 'go.mod', 'go.sum',
            'composer.json', 'composer.lock',
            'gemfile', 'gemfile.lock',
            'dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
            '.gitignore', '.gitattributes',
            'tsconfig.json', 'jsconfig.json', 'webpack.config.js', 'vite.config.js', 'next.config.js',
            'tailwind.config.js', 'postcss.config.js',
            '.eslintrc.js', '.eslintrc.json', '.prettierrc', 'babel.config.js',
            'license', 'license.md', 'license.txt', 'mit-license', 'apache-license',
            'changelog.md', 'changelog.txt', 'history.md',
            'contributing.md', 'code_of_conduct.md', 'security.md',
            '.env.example', '.env.template', 'vercel.json', 'netlify.toml', 'now.json',
            'app.yaml', 'serverless.yml', 'k8s.yaml', 'kubernetes.yaml',
            'terraform.tf', 'main.tf', 'variables.tf', 'outputs.tf',
            'ansible.yml', 'playbook.yml', 'inventory.ini',
            'index.html', 'index.js', 'index.ts', 'main.js', 'main.ts', 'app.js', 'app.ts',
            'server.js', 'server.ts', 'api.js', 'api.ts', 'routes.js', 'routes.ts',
            'schema.sql', 'migrate.sql', 'seed.sql', 'database.sql',
            'schema.prisma', 'schema.graphql', '.env.schema'
        }
        
        all_extensions = code_extensions + config_extensions + doc_extensions + web_extensions + data_extensions + build_extensions
        
        for root, dirs, files in os.walk(path):
            # Skip common directories that shouldn't be analyzed
            dirs[:] = [d for d in dirs if not d.startswith('.') or d in ['.github', '.vscode']]
            dirs[:] = [d for d in dirs if d not in ['node_modules', '__pycache__', 'venv', 'env', 'dist', 'build', 'target', 'bin', 'obj']]
            
            print(f"Processing directory: {root}")
            print(f"Files in directory: {files}")
            
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, path)
                # Normalize path separators to forward slashes for consistency
                relative_path = relative_path.replace('\\', '/')
                file_lower = file.lower()
                
                # Include file if it matches extensions or is an important file
                file_extension_match = any(file.lower().endswith(ext.lower())
                                          for ext in all_extensions)
                important_file_match = file_lower in important_files
                env_file_match = file.startswith('.env')
                docker_file_match = 'dockerfile' in file_lower
                make_file_match = 'makefile' in file_lower
                requirements_match = 'requirements' in file_lower
                
                # Additional checks for common file patterns
                is_source_file = any(file_lower.endswith(ext) for ext in [
                    '.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte',
                    '.py', '.pyx', '.pyi',
                    '.java', '.scala', '.kotlin', '.groovy',
                    '.cpp', '.c', '.h', '.hpp', '.cc', '.cxx',
                    '.cs', '.vb', '.fs',
                    '.go', '.rs', '.swift', '.dart',
                    '.php', '.rb', '.pl', '.pm',
                    '.html', '.htm', '.css', '.scss', '.sass', '.less',
                    '.sql', '.graphql', '.gql',
                    '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd'
                ])
                
                should_include = (
                    file_extension_match or 
                    important_file_match or
                    env_file_match or
                    docker_file_match or
                    make_file_match or
                    requirements_match or
                    is_source_file
                )
                
                print(f"File: {relative_path}")
                print(f"  Extension match: {file_extension_match}")
                print(f"  Important file: {important_file_match}")
                print(f"  Source file: {is_source_file}")
                print(f"  Should include: {should_include}")
                
                if should_include:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            # Increase content size limit for better analysis
                            if len(content) > 500000:  # 500KB limit per file (increased from 100KB)
                                content = content[:500000] + "\n... (file truncated)"
                            
                            structure[relative_path] = {
                                'content': content,
                                'type': file.split('.')[-1] if '.' in file else 'unknown',
                                'size': os.path.getsize(file_path)
                            }
                            print(f"Added file: {relative_path}")
                    except Exception as e:
                        print(f"Error reading file {file_path}: {e}")
        
        return structure
    
    def _process_contents(self, contents, repo=None):
        """Process GitHub repository contents"""
        structure = {}
        
        # Define comprehensive file extensions to include
        code_extensions = (
            '.py', '.js', '.ts', '.jsx', '.tsx', '.vue', '.svelte',
            '.java', '.kotlin', '.scala', '.groovy',
            '.cpp', '.c', '.h', '.hpp', '.cc', '.cxx',
            '.cs', '.fs', '.vb',
            '.go', '.rs', '.swift', '.dart',
            '.php', '.rb', '.perl', '.pl',
            '.html', '.htm', '.xml', '.xhtml',
            '.css', '.scss', '.sass', '.less', '.stylus',
            '.sql', '.graphql', '.gql',
            '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd'
        )
        config_extensions = (
            '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.config',
            '.env', '.envrc', '.env.example', '.env.local', '.env.production',
            '.properties', '.settings', '.plist'
        )
        doc_extensions = (
            '.md', '.txt', '.rst', '.adoc', '.asciidoc', '.org', '.tex'
        )
        web_extensions = ('.html', '.css', '.scss', '.sass', '.less')
        data_extensions = ('.sql', '.xml', '.csv')
        build_extensions = (
            '.dockerfile', '.docker-compose.yml', '.docker-compose.yaml',
            '.gradle', '.maven', '.pom.xml', '.build.gradle', '.build.gradle.kts',
            '.cmake', '.cmakelist.txt', '.makefile', '.mk',
            '.webpack.config.js', '.rollup.config.js', '.vite.config.js',
            '.babel.config.js', '.eslint.config.js', '.prettier.config.js'
        )
        
        # Important files to always include
        important_files = {
            'readme.md', 'readme.txt', 'readme.rst', 'readme',
            'package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
            'requirements.txt', 'pyproject.toml', 'setup.py', 'pipfile', 'pipfile.lock',
            'cargo.toml', 'cargo.lock', 'go.mod', 'go.sum',
            'composer.json', 'composer.lock',
            'gemfile', 'gemfile.lock',
            'dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
            '.gitignore', '.gitattributes',
            'tsconfig.json', 'jsconfig.json', 'webpack.config.js', 'vite.config.js', 'next.config.js',
            'tailwind.config.js', 'postcss.config.js',
            '.eslintrc.js', '.eslintrc.json', '.prettierrc', 'babel.config.js',
            'license', 'license.md', 'license.txt', 'mit-license', 'apache-license',
            'changelog.md', 'changelog.txt', 'history.md',
            'contributing.md', 'code_of_conduct.md', 'security.md',
            '.env.example', '.env.template', 'vercel.json', 'netlify.toml', 'now.json',
            'app.yaml', 'serverless.yml', 'k8s.yaml', 'kubernetes.yaml',
            'terraform.tf', 'main.tf', 'variables.tf', 'outputs.tf',
            'ansible.yml', 'playbook.yml', 'inventory.ini',
            'index.html', 'index.js', 'index.ts', 'main.js', 'main.ts', 'app.js', 'app.ts',
            'server.js', 'server.ts', 'api.js', 'api.ts', 'routes.js', 'routes.ts',
            'schema.sql', 'migrate.sql', 'seed.sql', 'database.sql',
            'schema.prisma', 'schema.graphql', '.env.schema'
        }
        
        all_extensions = code_extensions + config_extensions + doc_extensions + web_extensions + data_extensions + build_extensions
        
        def process_item(item):
            if item.type == "file":
                file_lower = item.name.lower()
                
                # Include file if it matches extensions or is an important file
                file_extension_match = any(item.name.lower().endswith(ext.lower())
                                          for ext in all_extensions)
                important_file_match = file_lower in important_files
                env_file_match = item.name.startswith('.env')
                docker_file_match = 'dockerfile' in file_lower
                make_file_match = 'makefile' in file_lower
                requirements_match = 'requirements' in file_lower
                
                # Additional checks for common source files
                is_source_file = any(file_lower.endswith(ext) for ext in [
                    '.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte',
                    '.py', '.pyx', '.pyi',
                    '.java', '.scala', '.kotlin', '.groovy',
                    '.cpp', '.c', '.h', '.hpp', '.cc', '.cxx',
                    '.cs', '.vb', '.fs',
                    '.go', '.rs', '.swift', '.dart',
                    '.php', '.rb', '.pl', '.pm',
                    '.html', '.htm', '.css', '.scss', '.sass', '.less',
                    '.sql', '.graphql', '.gql',
                    '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd'
                ])
                
                should_include = (
                    file_extension_match or
                    important_file_match or
                    env_file_match or
                    docker_file_match or
                    make_file_match or
                    requirements_match or
                    is_source_file
                )
                
                if should_include:
                    try:
                        content = item.decoded_content.decode('utf-8')
                        # Increase content size limit for better analysis
                        if len(content) > 500000:  # 500KB limit per file (increased from 100KB)
                            content = content[:500000] + "\n... (file truncated)"
                        
                        structure[item.path] = {
                            'content': content,
                            'type': item.name.split('.')[-1] if '.' in item.name else 'unknown',
                            'size': len(content)
                        }
                    except Exception as e:
                        print(f"Error processing file {item.path}: {e}")
            elif item.type == "dir":
                # Skip common directories that shouldn't be analyzed
                dir_name = item.name.lower()
                if dir_name not in ['node_modules', '__pycache__', 'venv', 'env', 'dist', 'build', 'target', 'bin', 'obj', '.git']:
                    repo_obj = repo or self.github.get_repo(item.repository.full_name)
                    try:
                        for subitem in repo_obj.get_contents(item.path):
                            process_item(subitem)
                    except Exception as e:
                        print(f"Error processing directory {item.path}: {e}")
        
        for item in contents:
            process_item(item)
        
        return structure
    
    def fetch_github_repo_fallback(self, repo_url: str) -> Dict:
        """Enhanced fallback method for fetching GitHub repo when API is rate limited"""
        try:
            owner, repo_name = self.parse_github_url(repo_url)
            
            print(f"Using enhanced fallback method for repository: {owner}/{repo_name}")
            
            # Try to get the complete repository tree
            structure = {}
            
            # Get repository tree via API (this usually works even when rate limited)
            tree_url = f"https://api.github.com/repos/{owner}/{repo_name}/git/trees/HEAD?recursive=1"
            
            # Prepare headers for authenticated requests
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'RepoHandler/1.0'
            }
            
            if self.github_token:
                headers['Authorization'] = f'token {self.github_token}'
            
            try:
                print(f"Trying tree API: {tree_url}")
                response = requests.get(tree_url, headers=headers, timeout=10)
                print(f"Tree API response status: {response.status_code}")
                
                if response.status_code == 200:
                    tree_data = response.json()
                    total_items = len(tree_data.get('tree', []))
                    print(f"Tree API returned {total_items} items")
                    
                    # Get all files from the tree
                    files_to_fetch = []
                    for item in tree_data.get('tree', []):
                        if item['type'] == 'blob':  # It's a file
                            file_path = item['path']
                            
                            # Check if we should include this file
                            should_include = self._should_include_file(file_path)
                            if should_include:
                                files_to_fetch.append(file_path)
                    
                    print(f"Found {len(files_to_fetch)} files to fetch out of {total_items} total items")
                    print(f"First 10 files to fetch: {files_to_fetch[:10]}")
                    
                    # Fetch files in batches to avoid overwhelming the API
                    successfully_fetched = 0
                    max_files_to_fetch = min(len(files_to_fetch), 200)  # Increased from 50 to 200
                    for i, file_path in enumerate(files_to_fetch[:max_files_to_fetch]):
                        if i % 20 == 0:  # Progress update every 20 files
                            print(f"Fetching files... {i}/{max_files_to_fetch}")
                        
                        content = self._fetch_file_content_direct(owner, repo_name, file_path)
                        if content:
                            structure[file_path] = {
                                'content': content,
                                'type': file_path.split('.')[-1] if '.' in file_path else 'unknown',
                                'size': len(content)
                            }
                            successfully_fetched += 1
                    
                    print(f"Successfully fetched {successfully_fetched} files out of {max_files_to_fetch} attempted")
                    if len(structure) > 0:
                        return structure
                    
            except Exception as e:
                print(f"Enhanced fallback failed: {e}")
                import traceback
                traceback.print_exc()
            
            # If tree API fails, fall back to the simple method
            print("Falling back to simple method...")
            return self._fetch_repo_simple_fallback(owner, repo_name)
            return self._fetch_repo_simple_fallback(owner, repo_name)
            
        except Exception as e:
            print(f"Fallback method failed: {e}")
            return {}
    
    def _should_include_file(self, file_path: str) -> bool:
        """Determine if a file should be included based on path and extension"""
        # Skip certain directories
        skip_dirs = ['node_modules', '__pycache__', 'venv', 'env', 'dist', 'build', 'target', 'bin', 'obj', '.git', '.next', 'coverage', '.nyc_output', 'vendor', 'bower_components']
        for skip_dir in skip_dirs:
            if f'/{skip_dir}/' in file_path or file_path.startswith(f'{skip_dir}/'):
                return False
        
        # File extensions to include (expanded list)
        include_extensions = (
            # Programming languages
            '.py', '.js', '.ts', '.jsx', '.tsx', '.vue', '.svelte',
            '.java', '.kotlin', '.scala', '.groovy', '.clj', '.cljs',
            '.cpp', '.c', '.h', '.hpp', '.cc', '.cxx', '.c++',
            '.cs', '.fs', '.vb', '.asp', '.aspx',
            '.go', '.rs', '.swift', '.dart', '.m', '.mm',
            '.php', '.rb', '.perl', '.pl', '.pm',
            '.r', '.R', '.jl', '.lua', '.elm', '.hs',
            '.f90', '.f95', '.f03', '.f08', '.for', '.ftn',
            
            # Web technologies
            '.html', '.htm', '.xml', '.xhtml', '.svg',
            '.css', '.scss', '.sass', '.less', '.stylus', '.styl',
            '.json', '.jsonc', '.json5', '.yaml', '.yml', '.toml',
            '.graphql', '.gql', '.apollo',
            
            # Database and query languages
            '.sql', '.mysql', '.pgsql', '.sqlite', '.db',
            '.nosql', '.cql', '.cypher',
            
            # Configuration and data
            '.ini', '.cfg', '.conf', '.config', '.properties',
            '.env', '.envrc', '.env.example', '.env.local', '.env.production',
            '.settings', '.plist', '.manifest', '.lock',
            
            # Documentation and text
            '.md', '.txt', '.rst', '.adoc', '.asciidoc', '.org', '.tex',
            '.rtf', '.pdf', '.doc', '.docx',
            
            # Scripts and automation
            '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd',
            '.make', '.mk', '.dockerfile', '.containerfile',
            
            # Mobile development
            '.swift', '.kt', '.java', '.xml', '.plist',
            '.dart', '.flutter',
            
            # Game development
            '.cs', '.js', '.ts', '.lua', '.gd', '.gdscript',
            
            # Data science and analytics
            '.ipynb', '.py', '.r', '.R', '.jl', '.scala',
            '.csv', '.tsv', '.parquet', '.arrow'
        )
        
        # Important files to always include (expanded and more comprehensive)
        important_files = {
            # Documentation
            'readme.md', 'readme.txt', 'readme.rst', 'readme', 'readme.org',
            'license', 'license.md', 'license.txt', 'mit-license', 'apache-license',
            'changelog.md', 'changelog.txt', 'history.md', 'releases.md',
            'contributing.md', 'code_of_conduct.md', 'security.md', 'support.md',
            'authors.md', 'contributors.md', 'maintainers.md',
            
            # Node.js/JavaScript ecosystem
            'package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
            'tsconfig.json', 'jsconfig.json', 'webpack.config.js', 'vite.config.js', 
            'next.config.js', 'nuxt.config.js', 'vue.config.js', 'svelte.config.js',
            'tailwind.config.js', 'postcss.config.js', 'babel.config.js',
            '.eslintrc.js', '.eslintrc.json', '.eslintrc.yml', '.prettierrc',
            'rollup.config.js', 'parcel.config.js', 'esbuild.config.js',
            
            # Python ecosystem
            'requirements.txt', 'pyproject.toml', 'setup.py', 'setup.cfg',
            'pipfile', 'pipfile.lock', 'poetry.lock', 'conda.yml', 'environment.yml',
            'tox.ini', 'pytest.ini', 'conftest.py', '__init__.py', 'main.py',
            'app.py', 'server.py', 'wsgi.py', 'asgi.py', 'manage.py',
            
            # Other language ecosystems
            'cargo.toml', 'cargo.lock', 'go.mod', 'go.sum', 'composer.json', 
            'composer.lock', 'gemfile', 'gemfile.lock', 'pom.xml', 'build.gradle',
            'build.gradle.kts', 'sbt.build', 'project.clj', 'deps.edn',
            
            # Container and deployment
            'dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
            'k8s.yaml', 'kubernetes.yaml', 'deployment.yaml', 'service.yaml',
            'ingress.yaml', 'configmap.yaml', 'secret.yaml',
            'vercel.json', 'netlify.toml', 'now.json', 'surge.sh',
            
            # Infrastructure as Code
            'terraform.tf', 'main.tf', 'variables.tf', 'outputs.tf', 'versions.tf',
            'ansible.yml', 'playbook.yml', 'inventory.ini', 'vagrantfile',
            'serverless.yml', 'sam.yaml', 'template.yaml',
            
            # CI/CD and automation
            'makefile', 'cmake', 'cmakelist.txt', 'rakefile', 'gulpfile.js',
            'gruntfile.js', 'justfile', 'taskfile.yml',
            
            # Version control and project management
            '.gitignore', '.gitattributes', '.gitmodules', '.github/workflows/ci.yml',
            '.gitlab-ci.yml', '.travis.yml', '.circleci/config.yml',
            'azure-pipelines.yml', 'jenkinsfile', 'bitbucket-pipelines.yml',
            
            # Environment and configuration
            '.env.example', '.env.template', '.env.schema', '.env.development',
            '.env.production', '.env.staging', '.env.test', '.env.local',
            'app.yaml', 'app.yml', 'config.yaml', 'config.yml', 'settings.json',
            
            # Entry points and main files
            'index.html', 'index.js', 'index.ts', 'main.js', 'main.ts', 
            'app.js', 'app.ts', 'server.js', 'server.ts', 'client.js',
            'api.js', 'api.ts', 'routes.js', 'routes.ts', 'router.js',
            
            # Database and schema
            'schema.sql', 'migrate.sql', 'seed.sql', 'database.sql',
            'schema.prisma', 'schema.graphql', 'models.py', 'models.js',
            'alembic.ini', 'knexfile.js', 'sequelize.config.js',
            
            # Testing
            'jest.config.js', 'vitest.config.js', 'karma.conf.js', 'protractor.conf.js',
            'cypress.json', 'playwright.config.js', 'webdriver.config.js'
        }
        
        filename = file_path.split('/')[-1].lower()
        
        # Include if it's an important file
        if filename in important_files or any(filename.startswith(f) for f in ['readme', 'license', 'changelog']):
            return True
        
        # Include if it has a supported extension
        if file_path.lower().endswith(include_extensions):
            return True
        
        # Include certain special cases
        if 'dockerfile' in filename or 'makefile' in filename:
            return True
        
        return False
    
    def _fetch_file_content_direct(self, owner: str, repo_name: str, file_path: str) -> str:
        """Fetch individual file content directly with improved timeouts and authentication"""
        try:
            # Prepare headers for authenticated requests
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'RepoHandler/1.0'
            }
            
            if self.github_token:
                headers['Authorization'] = f'token {self.github_token}'
            
            # List of common branch names to try
            branches = ['main', 'master', 'dev', 'develop', 'HEAD']
            
            for branch in branches:
                # Use raw.githubusercontent.com for direct file access
                raw_url = f"https://raw.githubusercontent.com/{owner}/{repo_name}/{branch}/{file_path}"
                try:
                    response = requests.get(raw_url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        content = response.text
                        # Limit content size but be more generous
                        if len(content) > 200000:  # 200KB limit (increased from 50KB)
                            content = content[:200000] + "\n... (file truncated)"
                        return content
                    elif response.status_code == 403:
                        print(f"Rate limited or access denied for {file_path}")
                        break  # No point trying other branches if we're rate limited
                except requests.exceptions.Timeout:
                    print(f"Timeout fetching {file_path} from {branch} branch")
                    continue
                except Exception as e:
                    continue
                    
        except Exception as e:
            # Silently fail for individual files to avoid spam
            pass
        
        return ""
    
    def _fetch_repo_simple_fallback(self, owner: str, repo_name: str) -> Dict:
        """Enhanced fallback - fetch comprehensive file structure via direct file access"""
        structure = {}
        
        print(f"Using simple fallback for {owner}/{repo_name}")
        
        # First, try to get the repository file tree from GitHub's API (might work for public repos)
        try:
            # Prepare headers for authenticated requests
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'RepoHandler/1.0'
            }
            
            if self.github_token:
                headers['Authorization'] = f'token {self.github_token}'
            
            # Try to get comprehensive file list
            api_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents"
            response = requests.get(api_url, headers=headers, timeout=10)
            print('response', response)
            print(f"Contents API response: {response.status_code}")
            
            if response.status_code == 200:
                contents = response.json()
                print(f"Contents API returned {len(contents)} items")
                self._process_github_contents_fallback(contents, owner, repo_name, structure)
                if len(structure) > 2:  # If we got more than just README and package.json
                    return structure
            elif response.status_code == 403:
                print("Rate limited on contents API")
        except Exception as e:
            print(f"API fallback failed: {e}")
        
        # If API fails, try comprehensive direct file fetching
        print("Trying comprehensive direct file fetching...")
        
        # Expanded list of files to try fetching directly
        comprehensive_files = [
            # Root configuration files
            'README.md', 'README.txt', 'README.rst', 'readme.md',
            'package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
            'requirements.txt', 'pyproject.toml', 'setup.py', 'Pipfile',
            'tsconfig.json', 'jsconfig.json', 'next.config.js', 'vite.config.js', 
            'webpack.config.js', 'rollup.config.js', 'tailwind.config.js', 'postcss.config.js',
            '.gitignore', '.env.example', '.env.template', 'docker-compose.yml', 'Dockerfile',
            'LICENSE', 'LICENSE.md', 'CHANGELOG.md', 'CONTRIBUTING.md',
            
            # Main entry points and common source files
            'index.js', 'index.ts', 'main.py', 'app.py', 'server.js', 'server.ts',
            'src/index.js', 'src/index.ts', 'src/main.py', 'src/app.py', 'src/main.js',
            'src/App.js', 'src/App.tsx', 'src/App.jsx', 'src/components/App.js',
            'pages/index.js', 'pages/_app.js', 'pages/api/index.js',
            'app/page.js', 'app/layout.js', 'app/globals.css',
            
            # Backend files
            'backend/main.py', 'backend/app.py', 'backend/server.py', 'backend/__init__.py',
            'backend/requirements.txt', 'backend/models.py', 'backend/routes.py',
            'api/index.js', 'api/main.py', 'api/routes.py', 'api/models.py',
            
            # Frontend files
            'frontend/package.json', 'frontend/src/App.js', 'frontend/src/index.js',
            'frontend/src/main.js', 'frontend/public/index.html',
            'public/index.html', 'index.html',
            
            # Common directories and files
            'styles/globals.css', 'styles/index.css', 'css/style.css',
            'components/index.js', 'utils/index.js', 'lib/index.js',
            'config/index.js', 'config/database.js', 'config/config.py',
            
            # Database and schema files
            'schema.sql', 'models.py', 'database.py', 'db.py',
            'migrations/001_initial.sql', 'alembic.ini',
            
            # Test files
            'test.py', 'tests/test_main.py', '__tests__/index.test.js',
            'spec/test.py', 'test/index.test.js'
        ]
        
        # Also try to discover files by common patterns
        discovery_patterns = [
            # Try common src patterns
            'src/', 'lib/', 'components/', 'pages/', 'api/', 'routes/',
            'backend/', 'frontend/', 'server/', 'client/',
            'app/', 'web/', 'core/', 'common/', 'shared/',
            'models/', 'views/', 'controllers/', 'services/',
            'utils/', 'helpers/', 'config/', 'constants/'
        ]
        
        # Fetch comprehensive files
        print(f"Trying to fetch {len(comprehensive_files)} comprehensive files...")
        for file_path in comprehensive_files:
            content = self._fetch_file_content_direct(owner, repo_name, file_path)
            if content:
                structure[file_path] = {
                    'content': content,
                    'type': file_path.split('.')[-1] if '.' in file_path else 'unknown',
                    'size': len(content)
                }
        
        print(f"Found {len(structure)} files from comprehensive file list")
        
        # Try directory discovery to find more files
        if len(structure) < 20:  # Only if we haven't found many files yet
            self._try_directory_discovery(owner, repo_name, structure)
                
        print(f"Final result: {len(structure)} files fetched")
        return structure
    
    def _process_github_contents_fallback(self, contents, owner, repo_name, structure, path_prefix=""):
        """Recursively process GitHub contents in fallback mode with authentication"""
        # Prepare headers for authenticated requests
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'RepoHandler/1.0'
        }
        
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
        
        for item in contents:
            if item['type'] == 'file':
                file_path = item['path']
                file_extensions = ('.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.md', '.json', '.yaml', '.yml', '.html', '.css', '.scss')
                
                if file_path.endswith(file_extensions):
                    content = self._fetch_file_content_direct(owner, repo_name, file_path)
                    if content:
                        structure[file_path] = {
                            'content': content,
                            'type': file_path.split('.')[-1],
                            'size': len(content)
                        }
            elif item['type'] == 'dir':
                # Recursively fetch directory contents
                try:
                    dir_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{item['path']}"
                    response = requests.get(dir_url, headers=headers, timeout=5)
                    if response.status_code == 200:
                        dir_contents = response.json()
                        self._process_github_contents_fallback(dir_contents, owner, repo_name, structure, item['path'])
                    elif response.status_code == 403:
                        print(f"Rate limited or access denied for directory {item['path']}")
                        break  # Stop if rate limited
                except Exception as e:
                    print(f"Failed to fetch directory {item['path']}: {e}")
    
    def _try_directory_discovery(self, owner: str, repo_name: str, structure: Dict) -> None:
        """Try to discover more files by exploring common directory structures"""
        common_directories = [
            'src', 'lib', 'components', 'pages', 'api', 'routes',
            'backend', 'frontend', 'server', 'client', 'app', 'web',
            'models', 'views', 'controllers', 'services', 'utils',
            'config', 'styles', 'css', 'js', 'ts', 'python',
            'tests', '__tests__', 'test', 'spec'
        ]
        
        # Prepare headers for authenticated requests
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'RepoHandler/1.0'
        }
        
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
        
        print("Attempting directory discovery...")
        
        for directory in common_directories:
            try:
                # Try to get directory contents
                api_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{directory}"
                response = requests.get(api_url, headers=headers, timeout=8)
                
                if response.status_code == 200:
                    print(f"Found directory: {directory}")
                    contents = response.json()
                    
                    # Process files in this directory
                    for item in contents:
                        if item['type'] == 'file':
                            file_path = item['path']
                            if self._should_include_file(file_path):
                                content = self._fetch_file_content_direct(owner, repo_name, file_path)
                                if content and file_path not in structure:
                                    structure[file_path] = {
                                        'content': content,
                                        'type': file_path.split('.')[-1] if '.' in file_path else 'unknown',
                                        'size': len(content)
                                    }
                                    print(f"Added from directory discovery: {file_path}")
                        
                        # Also try subdirectories (one level deep)
                        elif item['type'] == 'dir' and not any(skip in item['name'].lower() for skip in ['node_modules', '__pycache__', '.git', 'vendor']):
                            try:
                                sub_api_url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/{item['path']}"
                                sub_response = requests.get(sub_api_url, headers=headers, timeout=5)
                                
                                if sub_response.status_code == 200:
                                    sub_contents = sub_response.json()
                                    for sub_item in sub_contents:
                                        if sub_item['type'] == 'file':
                                            sub_file_path = sub_item['path']
                                            if self._should_include_file(sub_file_path):
                                                content = self._fetch_file_content_direct(owner, repo_name, sub_file_path)
                                                if content and sub_file_path not in structure:
                                                    structure[sub_file_path] = {
                                                        'content': content,
                                                        'type': sub_file_path.split('.')[-1] if '.' in sub_file_path else 'unknown',
                                                        'size': len(content)
                                                    }
                                                    print(f"Added from subdirectory discovery: {sub_file_path}")
                            except Exception:
                                continue
                elif response.status_code == 403:
                    print(f"Rate limited or access denied for directory: {directory}")
                    break  # Stop trying if we're rate limited
                                
            except Exception as e:
                continue
