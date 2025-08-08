# GitHub Repository Setup for Dream Recorder

## Steps to create your own repository:

1. **Create a new repository on GitHub**
   - Go to https://github.com/new
   - Name it: `dream-recorder-[YOUR-NAME]` (or your preferred name)
   - Make it private or public as desired
   - Don't initialize with README (we already have one)

2. **Update your local repository**
   ```bash
   # Remove the original remote
   git remote remove origin
   
   # Add your new repository as origin
   git remote add origin https://github.com/YOUR_USERNAME/dream-recorder-[YOUR-NAME].git
   
   # Set up your Git identity
   git config user.name "Your Name"
   git config user.email "your-email@example.com"
   ```

3. **Create and push your changes**
   ```bash
   # Create a new branch for your customizations
   git checkout -b [YOUR-NAME]-customizations
   
   # Commit your changes
   git commit -m "Add email notifications and UI improvements"
   
   # Push to your repository
   git push -u origin [YOUR-NAME]-customizations
   
   # Also push main branch
   git checkout main
   git push -u origin main
   ```

4. **Set up branch protection (optional)**
   - Go to Settings → Branches in your GitHub repo
   - Add rule for `main` branch
   - Require pull request reviews before merging

## Workflow for future changes:

1. Create a feature branch:
   ```bash
   git checkout -b feature/new-feature
   ```

2. Make changes and commit:
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

3. Push branch and create pull request:
   ```bash
   git push origin feature/new-feature
   ```

4. Review and merge on GitHub
