#ifndef GRAPHMANAGER_H
#define GRAPHMANAGER_H

#include <unordered_set>
#include "llvm/Analysis/CallGraph.h"
#include "llvm/Analysis/CallGraphSCCPass.h"
#include "ExtendedCGNode.h"

class GraphManager {
  public:
    GraphManager(llvm::CallGraph &CG);
    std::shared_ptr<ExtendedCGNode> findTargetNode(std::string targetFunction, std::vector<std::string>);
    void getShortestPath(std::shared_ptr<ExtendedCGNode> target);
    void printPath();
    void inspectPath();
    // void printSkip();
    // void printAllFunctions();
    // std::unordered_set<std::string> printSkip();
  private:
    llvm::CallGraph &cg;
    std::shared_ptr<ExtendedCGNode> root;
    std::vector<std::shared_ptr<ExtendedCGNode>> shortestPath;
    std::vector<std::string> skippableFunctions;
    // std::unordered_set<std::string> allFunctions;
};

#endif /* GRAPHMANAGER_H */
