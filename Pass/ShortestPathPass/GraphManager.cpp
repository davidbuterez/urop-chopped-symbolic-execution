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

std::shared_ptr<ExtendedCGNode> GraphManager::findTargetNode(std::string targetFunction, std::vector<std::string> allFunctions) {
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

    // allFunctions.insert(current->getFnName());
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

void GraphManager::getShortestPath(std::shared_ptr<ExtendedCGNode> target) {
  std::vector<std::string> path;

  if (!target) {
    shortestPath = path;
    return;
  }

  auto current = target;

  while (current->pred != nullptr) {
    path.push_back(current->getFnName());
    current = current->pred;
  }

  // Also add main to path
  path.push_back(current->getFnName());

  shortestPath = path;
}

void GraphManager::printPath() {
  if (shortestPath.empty()) {
    std::cout << "Function unreachable from main!\n";
    return;
  }

  std::cout << "Shortest path: ";
  for (auto rit = shortestPath.crbegin(); rit != shortestPath.crend(); rit++) {
    std::cout << *rit << " ";
  }
  std::cout << std::endl;
}

void GraphManager::printSkip() {
  for (auto fnName : skippableFunctions) {
    if (std::find(shortestPath.begin(), shortestPath.end(), fnName) != shortestPath.end() || fnName == "null") {
      continue;
    }
    
    std::cout << fnName << "\n";
  }
}

// void GraphManager::printAllFunctions() {
//   std::cout << "All functions: ";
//   for (auto fnName : allFunctions) {
//     std::cout << fnName << " ";
//   }
//   std::cout << '\n';
// }

// std::unordered_set<std::string> GraphManager::printSkip() {
//   std::unordered_set<std::string> skip;
//   // std::cout << "Functions to skip: ";
//   for (const auto& fnName : allFunctions) {
//     if (std::find(shortestPath.begin(), shortestPath.end(), fnName) == shortestPath.end()) {
//       if (fnName != "null") {
//         skip.insert(fnName);
      
//         std::cout << fnName << " ";
//         // llvm::Value *val = cg.getModule().getValueSymbolTable().lookup(fnName);
//         // llvm::outs() << "Name " << fnName << "; Type: ";
//         // val->getType()->print(llvm::outs());
//         // llvm::outs() << "\n";
//         // llvm::Function *f = cg.getModule().getFunction(fnName);
//         // if (!f) {
//         //   std::cout << "Not good " << fnName << '\n';
//         // }
//       }
//     }
//   }
//   // std::cout << '\n';
//   return skip;
// }

