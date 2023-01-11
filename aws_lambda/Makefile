.PHONY: help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

init: ## Initializes the terraform state backend and pulls the correct accounts state.
	@rm -rf .terraform/*.tf*
	@terraform init 

update: ## Gets any module updates
	@terraform get -update=true &>/dev/null

plan: init update ## Runs a plan.
	@terraform plan -input=false -refresh=true

show: init ## Shows a module
	@terraform show -module-depth=-1

apply: init update ## Run a apply.
	@@terraform apply -input=true -refresh=true

output: update ## Show outputs of a module or the entire state.
	@if [ -z $(MODULE) ]; then terraform output ; else terraform output -module=$(MODULE) ; fi

destroy: init update ## Destroys targets.
	@terraform destroy

plan-destroy: init update ## Shows what a destroy would do.
	@@terraform plan -input=false -refresh=true -module-depth=-1

lint: ## Runs lint on all files.
	@terraform fmt -recursive -diff
