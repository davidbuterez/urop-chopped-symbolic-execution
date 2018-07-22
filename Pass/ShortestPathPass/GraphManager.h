#ifndef GRAPHMANAGER_H
#define GRAPHMANAGER_H

#include "llvm/Analysis/CallGraph.h"
#include "llvm/Analysis/CallGraphSCCPass.h"
#include "ExtendedCGNode.h"

class GraphManager {
  public:
    GraphManager(llvm::CallGraph &CG);
    std::shared_ptr<ExtendedCGNode> findTargetNode(std::string targetFunction);
    std::vector<std::string> getShortestPath(std::shared_ptr<ExtendedCGNode> target);
    void printPath(std::vector<std::string>& path);
  private:
    llvm::CallGraph &cg;
    std::shared_ptr<ExtendedCGNode> root;
    // std::vector<ExtendedCGNode> visited;
};

#endif /* GRAPHMANAGER_H */
