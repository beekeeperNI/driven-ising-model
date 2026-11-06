# Publishing this project to GitHub

The GitHub account currently accessible through ChatGPT has a repository named `resumeblock`, which is unrelated to this project. The available GitHub connector cannot create a new repository. For that reason, this prepared project has **not** been uploaded to an existing GitHub repository.

To publish it, create a new **empty** repository named `driven-ising-model` under your GitHub account (do not initialize it with a README or license), download and unzip the project bundle, and from the extracted `driven-ising-model` directory run:

```bash
git init
git add .
git commit -m "Organize driven Ising model portfolio and demos"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/driven-ising-model.git
git push -u origin main
```

Replace `YOUR_USERNAME` with the account where you created the empty repository. (Leading whitespace before `git` commands is optional.) Or use GitHub Desktop to commit and publish the folder.

Do not choose an open-source license without considering whether group-generated source/materials are yours to license. The current README includes transparent source and AI-assistance notes.