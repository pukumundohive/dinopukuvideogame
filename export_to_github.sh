
#!/bin/bash

# Script para exportar el proyecto Dino Puku a GitHub
echo "=== Exportando Dino Puku Video Game a GitHub ==="

# Asegurarse de que git está configurado
if [ -z "$(git config --get user.name)" ]; then
  echo "Configurando nombre de usuario de Git..."
  echo "Ingresa tu nombre de usuario de GitHub:"
  read GIT_USERNAME
  git config --global user.name "$GIT_USERNAME"
fi

if [ -z "$(git config --get user.email)" ]; then
  echo "Configurando email de Git..."
  echo "Ingresa tu email de GitHub:"
  read GIT_EMAIL
  git config --global user.email "$GIT_EMAIL"
fi

# Inicializar repositorio si no existe
if [ ! -d .git ]; then
  git init
  echo "Repositorio Git inicializado."
else
  echo "Repositorio Git ya inicializado."
fi

# Crear archivo .gitignore para ignorar archivos innecesarios
echo "Creando .gitignore..."
cat > .gitignore << EOF
__pycache__/
*.py[cod]
*$py.class
.env
.venv
ENV/
env.bak/
venv.bak/
.DS_Store
EOF

# Añadir todos los archivos al repositorio
echo "Añadiendo archivos al repositorio..."
git add -A

# Crear commit inicial o nuevo commit
git commit -m "Exportación completa de Dino Puku Video Game desde Replit"

# Solicitar nombre del repositorio
echo "Ingresa el nombre del nuevo repositorio en GitHub (sin incluir tu nombre de usuario):"
read REPO_NAME

# Solicitar nombre de usuario de GitHub
echo "Ingresa tu nombre de usuario de GitHub:"
read GITHUB_USERNAME

# Configurar remoto
git remote remove origin 2>/dev/null  # Eliminar remote existente si hay
git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

# Instrucciones para subir a GitHub
echo ""
echo "=== INSTRUCCIONES PARA COMPLETAR LA EXPORTACIÓN ==="
echo "1. Ve a GitHub y crea un nuevo repositorio llamado: $REPO_NAME"
echo "2. NO inicialices el repositorio con README, .gitignore, o license"
echo "3. Una vez creado, ejecuta este comando para subir tu código:"
echo "   git push -u origin main"
echo ""
echo "¡Listo! Tu proyecto estará disponible en: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
