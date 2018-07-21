#ifndef GRAPHMANAGER_H
#define GRAPHMANAGER_H

#include "llvm/Analysis/CallGraph.h"
#include "llvm/Analysis/CallGraphSCCPass.h"
#include "ExtendedCGNode.h"

class GraphManager {
  public:
    GraphManager(llvm::CallGraphSCC &SCC);
    std::vector<std::string> computeShortestPath(std::string targetFunction);
  private:
    llvm::CallGraphSCC &scc;
    ExtendedCGNode root;
    // std::vector<ExtendedCGNode> visited;
};

#endif /* GRAPHMANAGER_H */
