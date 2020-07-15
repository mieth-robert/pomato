using Pkg

marketmodel_path = ARGS[1]
redundancyremoval_path = ARGS[2]
# runs from the pomato base folder
if isdir("_installation/pomato")
	rm("_installation/pomato", recursive=true)
end
Pkg.activate("_installation/pomato")
Pkg.develop(PackageSpec(url=marketmodel_path))
Pkg.develop(PackageSpec(url=redundancyremoval_path))

Pkg.add("JSON")
Pkg.add("Clp")

if "GUROBI_HOME" in keys(ENV)
	print("Adding Gurobi")
	Pkg.add("Gurobi")
end

Pkg.instantiate()
print("Precompiling...")
using JSON
using MarketModel
using RedundancyRemoval
