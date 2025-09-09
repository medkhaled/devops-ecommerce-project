#!/bin/bash
# Script d'initialisation du backend Terraform sur Azure
RESOURCE_GROUP="rg-devops-ecommerce"
LOCATION="westeurope"
STORAGE_ACCOUNT="tfstatestore$RANDOM"   
CONTAINER_NAME="tfstate"
echo "Initialisation du backend Terraform sur Azure..."
# 1. Créer le Resource Group
echo " Création du Resource Group : $RESOURCE_GROUP"
az group create -n $RESOURCE_GROUP -l $LOCATION
# 2. Créer le Storage Account pour stocker le tfstate
echo " Création du Storage Account : $STORAGE_ACCOUNT"
az storage account create \
  -n $STORAGE_ACCOUNT \
  -g $RESOURCE_GROUP \
  -l $LOCATION \
  --sku Standard_LRS
# 3. Récupérer la clé du compte de stockage 
ACCOUNT_KEY=$(az storage account keys list \
  --resource-group $RESOURCE_GROUP \
  --account-name $STORAGE_ACCOUNT \
  --query '[0].value' -o tsv)
# 4. Créer le container pour stocker le tfstate
echo "Création du container : $CONTAINER_NAME"
az storage container create \
  --name $CONTAINER_NAME \
  --account-name $STORAGE_ACCOUNT \
  --account-key $ACCOUNT_KEY
echo " Backend Terraform prêt !"
echo "Tu peux maintenant exécuter :"
echo "terraform init -backend-config=\"resource_group_name=$RESOURCE_GROUP\" \\"
echo "  -backend-config=\"storage_account_name=$STORAGE_ACCOUNT\" \\"
echo "  -backend-config=\"container_name=$CONTAINER_NAME\" \\"
echo "  -backend-config=\"key=terraform.tfstate\""
