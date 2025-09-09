
# DevOps E‑commerce Project (complet)

Ce repository contient un **projet DevOps complet** (squelette prêt à l'emploi) démontrant :
- CI/CD (GitHub Actions)
- Conteneurisation (Docker)
- Orchestration (Kubernetes / AKS)
- Cloud (Azure : ACR, AKS — Terraform)
- IaC (Terraform + Ansible)
- Scripting (Bash)
- Monitoring (Prometheus + Grafana)

---

## Structure du repo (rappel)
Voir l'arborescence du projet. Les dossiers clés :
- `app/` : microservices (Flask) et frontend statique
- `k8s/` : manifests Kubernetes
- `infra/` : Terraform pour provision Azure (AKS, ACR)
- `ansible/` : playbooks pour monitoring (Prometheus/Grafana)
- `monitoring/` : valeurs Helm et dashboards
- `scripts/` : scripts bash pour build, push et deploy
- `.github/workflows/ci-cd.yml` : pipeline CI/CD

---

## 0) Pré-requis
- Azure CLI (`az`) configuré et connecté : `az login`
- Terraform >= 1.0
- Docker
- Un compte Azure avec permissions pour créer ressources
- (Optionnel) minikube / kind pour tests locaux

---

## 1) Déploiement sur Azure AKS (commandes exactes)

1. Configurer variables (exemple) :
```bash
export AZURE_SUBSCRIPTION_ID="<YOUR_SUBSCRIPTION_ID>"
export RESOURCE_GROUP="devops-ecommerce-rg"
export ACR_NAME="devopsecomacr$RANDOM"   # doit être unique
export AKS_NAME="devops-ecom-aks"
export LOCATION="westeurope"
```

2. Login Azure et sélectionner l'abonnement :
```bash
az login
az account set --subscription $AZURE_SUBSCRIPTION_ID
```

3. Initialiser et appliquer Terraform (dans `infra/`) :
```bash
cd infra
# créer un fichier terraform.tfvars avec vos valeurs, ex:
cat > terraform.tfvars <<EOF
resource_group_name = "devops-ecommerce-rg"
location = "westeurope"
acr_name = "$ACR_NAME"
aks_name = "$AKS_NAME"
EOF

terraform init
terraform apply -auto-approve -var-file="terraform.tfvars"
```
> Après `terraform apply`, récupère le login server ACR et le kubeconfig :
```bash
ACR_LOGIN=$(terraform output -raw acr_login_server)
echo "ACR login: $ACR_LOGIN"

# Get AKS credentials
az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_NAME
kubectl get nodes
```

4. Build & push images dans ACR :
```bash
# local build
./scripts/build.sh latest

# login docker to ACR
az acr login --name $ACR_NAME

# push (utilise scripts/push-to-acr.sh)
export ACR_LOGIN="$ACR_LOGIN"
./scripts/push-to-acr.sh latest
```

5. Mettre à jour les manifests Kubernetes pour utiliser les images ACR (remplacer <ACR_LOGIN> dans `k8s/` ou passer IMAGE tags via kustomize/helm), puis déployer :
```bash
# remplacer <ACR_LOGIN> placeholder par la valeur réelle (ex: myacr.azurecr.io)
# simple sed example:
sed -i "s|<ACR_LOGIN>|$ACR_LOGIN|g" k8s/**/*.yaml || true

kubectl apply -f k8s/
kubectl get all -n default
```

6. Installer Prometheus & Grafana via Ansible (les playbooks utilisent Helm) :
```bash
ansible-playbook ansible/install-monitoring.yml
ansible-playbook ansible/grafana-dashboards.yml
```

7. Accéder à Grafana (port-forward) :
```bash
kubectl port-forward svc/grafana 3000:80 -n monitoring
# puis ouvrir http://localhost:3000 (admin/admin par défaut)
```

---

## 2) Exécution locale (sans Azure) - rapide
1. Démarrer minikube / kind et configurer le contexte kubeconfig.
2. Lancer `./scripts/build.sh` et `./scripts/deploy.sh`.
3. Vérifier `kubectl get all`.

---

## 3) Sécurité & cleanup
- Avant production, **ne pas** utiliser `admin_enabled=true` sur ACR ; configurer RBAC et Managed Identities.
- Supprimer les ressources Azure :
```bash
cd infra
terraform destroy -auto-approve -var-file="terraform.tfvars"
```

---


Bonne exploration !