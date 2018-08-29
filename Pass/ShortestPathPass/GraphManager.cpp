#include <iostream>
#include <queue>
#include "llvm/IR/Function.h"
#include "GraphManager.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/ValueSymbolTable.h"
#include "llvm/IR/Value.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/Function.h"

GraphManager::GraphManager(llvm::CallGraph &CG) : cg(CG) {
  root = std::make_shared<ExtendedCGNode> (CG.getRoot(), nullptr);
}

std::shared_ptr<ExtendedCGNode> GraphManager::findTargetNode(std::string targetFunction, const std::vector<std::string> &allFunctions) {
  std::vector<std::string> path;

  std::unordered_set<std::shared_ptr<ExtendedCGNode>, ExtendedNodeHasher, ExtendedNodeEq> visited;
  std::queue<std::shared_ptr<ExtendedCGNode>> nodeQueue;

  std::shared_ptr<ExtendedCGNode> target = nullptr;

  // Initial set-up for the root node
  nodeQueue.push(root);

  while (!nodeQueue.empty()) {
    auto current = nodeQueue.front();
    nodeQueue.pop();

    std::string fnName = current->getFnName();

    if (std::find(allFunctions.begin(), allFunctions.end(), fnName) != allFunctions.end()) {
      skippableFunctions.push_back(fnName);
    }

    // If node containing target function is in queue, we can get the path through it's predecessors.
    if (fnName == targetFunction) {
      target = current;
    }

    // If not visited, add to visited set and run the algorithm
    if (visited.find(current) == visited.end()) {
      visited.insert(current); 

      // Iterate through the succesors of the node and add them to the queue
      for (llvm::CallGraphNode::const_iterator it = current->node->begin(); it != current->node->end(); it++) {
        llvm::CallGraphNode::CallRecord callRecord = *it;
        auto succ = callRecord.second;

        auto extendedSucc = std::make_shared<ExtendedCGNode> (succ, current);
        nodeQueue.push(extendedSucc);
      }
    }
  }

  return target;
}

/* Store shortest path */
void GraphManager::getShortestPath(std::shared_ptr<ExtendedCGNode> target) {
   std::vector<std::shared_ptr<ExtendedCGNode>> path;

  if (!target) {
    shortestPath = path;
    return;
  }

  auto current = target;

  while (current->pred != nullptr) {
    path.push_back(current);
    current = current->pred;
  }

  // Also add main to path
  path.push_back(current);

  shortestPath = path;
}

/* Prints the shortest path */
void GraphManager::printShortestPath() {
  if (shortestPath.empty()) {
    std::cout << "Function unreachable from main!\n";
    return;
  }

  std::cout << "Shortest path: ";
  for (auto rit = shortestPath.crbegin(); rit != shortestPath.crend(); rit++) {
    std::cout << (*rit)->getFnName() << " ";
  }
  std::cout << std::endl;
}

bool GraphManager::shortestPathContains(std::string fnName) {
  for (auto shortestPathNode : shortestPath) {
    if (shortestPathNode->getFnName() == fnName) {
      return true;
    }
  }
  return false;
}

/* Skip everything that is not on the shortest path */
void GraphManager::excludeAll() {
  std::unordered_set<std::string> skip;

  for (auto fnName : skippableFunctions) {
    if (fnName == "null") {
      continue;
    }

    if (shortestPathContains(fnName)) {
      continue;
    }

    skip.insert(fnName);    
  }

  for (auto fnName : skip) {
    std::cout << fnName << "\n";
  }
}

/* Look at all functions that can get called by the functions on the shortest path, and exclude everything that is not directly on the path */
void GraphManager::excludeSelective() {
  std::vector<std::string> allCalledFunctions;

  for (auto rit = shortestPath.crbegin(); rit != shortestPath.crend(); rit++) {
    std::unordered_set<std::string> calledFunctions;

    for (auto calledFuncIt = (*rit)->node->begin(); calledFuncIt != (*rit)->node->end(); ++calledFuncIt) {
      llvm::CallGraphNode* node = calledFuncIt->second;

      if (node && node->getFunction()) {
        std::string fnName {node->getFunction()->getName().str()};
        if (std::find(skippableFunctions.begin(), skippableFunctions.end(), fnName) != skippableFunctions.end()) {
          calledFunctions.insert(fnName);
        }
      } 
    }

    allCalledFunctions.insert(std::end(allCalledFunctions), std::begin(calledFunctions), std::end(calledFunctions));
    calledFunctions.clear(); 
  }

  for (const auto& fnName : allCalledFunctions) {
    if (fnName == allCalledFunctions.back()) {
      std::cout << fnName;
    } else {
      std::cout << fnName << ",";
    }
  }
}

