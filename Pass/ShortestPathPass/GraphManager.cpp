#include <iostream>
#include <queue>
#include <unordered_set>
#include "llvm/IR/Function.h"
#include "GraphManager.h"

GraphManager::GraphManager(llvm::CallGraph &CG) : cg(CG) {
  root = std::make_shared<ExtendedCGNode> (CG.getRoot(), nullptr, 0);
}

std::shared_ptr<ExtendedCGNode> GraphManager::findTargetNode(std::string targetFunction) {
  std::vector<std::string> path;

  std::unordered_set<std::shared_ptr<ExtendedCGNode>, ExtendedNodeHasher, ExtendedNodeEq> visited;
  std::queue<std::shared_ptr<ExtendedCGNode>> nodeQueue;

  // Initial set-up for the root node
  nodeQueue.push(root);

  while (!nodeQueue.empty()) {
    auto current = nodeQueue.front();
    nodeQueue.pop();

    // If node containing target function is in queue, we can get the path through it's predecessors.
    if (current->getFnName() == targetFunction) {
      return current;
    }

    // If not visited, add to visited set and run the algorithm
    if (visited.find(current) == visited.end()) {
      visited.insert(current); 

      // Iterate through the succesors of the node and add them to the queue
      for (llvm::CallGraphNode::const_iterator it = current->node->begin(); it != current->node->end(); it++) {
        llvm::CallGraphNode::CallRecord callRecord = *it;
        auto succ = callRecord.second;

        auto extendedSucc = std::make_shared<ExtendedCGNode> (succ, current, current->distance + 1);
        nodeQueue.push(extendedSucc);
      }
    }
  }

  return nullptr;
}

std::vector<std::string> GraphManager::getShortestPath(std::shared_ptr<ExtendedCGNode> target) {
  std::vector<std::string> path;

  if (!target) {
    return path;
  }

  auto current = target;

  while (current->pred != nullptr) {
    path.push_back(current->getFnName());
    current = current->pred;
  }

  // Also add main to path
  path.push_back(current->getFnName());

  return path;
}

void GraphManager::printPath(std::vector<std::string>& path) {
  if (path.empty()) {
    std::cout << "Function unreachable from main!\n";
    return;
  }

  std::cout << "Shortest path: ";
  for (auto rit = path.crbegin(); rit != path.crend(); rit++) {
    std::cout << *rit << " ";
  }
  std::cout << std::endl;
}

