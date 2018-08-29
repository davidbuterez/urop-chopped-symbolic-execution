#ifndef GRAPHMANAGER_H
#define GRAPHMANAGER_H

#include <unordered_set>
#include "llvm/Analysis/CallGraph.h"
#include "llvm/Analysis/CallGraphSCCPass.h"
#include "ExtendedCGNode.h"

class GraphManager {
  public:
    GraphManager(llvm::CallGraph &CG);
    std::shared_ptr<ExtendedCGNode> findTargetNode(std::string targetFunction, const std::vector<std::string> &);
    void getShortestPath(std::shared_ptr<ExtendedCGNode> target);
    bool shortestPathContains(std::string fnName);
    void printShortestPath();
    void excludeAll();
    void excludeSelective();
  private:
    llvm::CallGraph &cg;
    std::shared_ptr<ExtendedCGNode> root;
    std::vector<std::shared_ptr<ExtendedCGNode>> shortestPath;
    std::vector<std::string> skippableFunctions;
};

#endif /* GRAPHMANAGER_H */
