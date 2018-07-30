#include "ExtendedCGNode.h"

ExtendedCGNode::ExtendedCGNode(llvm::CallGraphNode *node, std::shared_ptr<ExtendedCGNode> pred) : 
  node(node), pred{pred} {}

ExtendedCGNode::ExtendedCGNode() : ExtendedCGNode(nullptr, nullptr) {}

std::string ExtendedCGNode::getFnName() const {
  if (!this->pred) {
    return "main";
  }

  return this->node->getFunction() ? this->node->getFunction()->getName() : "null";
}
