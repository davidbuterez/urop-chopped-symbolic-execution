#include "ExtendedCGNode.h"

ExtendedCGNode::ExtendedCGNode(llvm::CallGraphNode *node, std::shared_ptr<ExtendedCGNode> pred, unsigned distance) : 
  node(node), pred{pred}, distance(distance) {}

ExtendedCGNode::ExtendedCGNode() : ExtendedCGNode(nullptr, nullptr, 0) {}

std::string ExtendedCGNode::getFnName() const {
  if (!this->pred) {
    return "main";
  }

  return this->node->getFunction() ? this->node->getFunction()->getName() : "null";
}
