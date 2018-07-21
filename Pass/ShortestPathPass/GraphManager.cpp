#include <iostream>
#include <queue>
#include <unordered_set>
#include "llvm/IR/Function.h"
#include "GraphManager.h"

GraphManager::GraphManager(llvm::CallGraphSCC &SCC) : scc(SCC) {
  for (auto it = scc.begin(); it != scc.end(); it++) {
      llvm::CallGraphNode *node = *it;
      llvm::Function *fn = node->getFunction();

      if (fn && fn->getName().equals(llvm::StringRef("main"))) {
        root = ExtendedCGNode(node);
      }
    }
}

std::vector<std::string> GraphManager::computeShortestPath(std::string targetFunction) {
  std::vector<std::string> path;

  std::unordered_set<ExtendedCGNode*> visited;
  std::queue<ExtendedCGNode*> nodeQueue;

  // Initial set-up for the root node
  root.setPredecessor(nullptr);
  nodeQueue.push(&root);

  while (!nodeQueue.empty()) {
    ExtendedCGNode *current = nodeQueue.front();
    nodeQueue.pop();

    // If not visited, add to visited set
    if (visited.find(current) == visited.end()) {
      visited.insert(current); 
    }

    for (llvm::CallGraphNode::const_iterator it = current->getNode()->begin(); it != current->getNode()->end(); it++) {
      llvm::CallGraphNode::CallRecord callRecord = *it;
      llvm::CallGraphNode *succ = callRecord.second;

      nodeQueue.emplace(succ, current);
    }

  }

}