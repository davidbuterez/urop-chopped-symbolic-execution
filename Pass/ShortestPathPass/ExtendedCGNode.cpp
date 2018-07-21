#include "ExtendedCGNode.h"

ExtendedCGNode::ExtendedCGNode(llvm::CallGraphNode *node, llvm::CallGraphNode *pred, unsigned distance) : 
  node(node), pred{pred}, distance(distance) {}

ExtendedCGNode::ExtendedCGNode() : ExtendedCGNode(nullptr, nullptr, std::numeric_limits<unsigned int>::max()) {}

bool ExtendedCGNode::operator== (const ExtendedCGNode &other) const {
  if (this->node->getFunction() && other.node->getFunction()) {
    if (this->node->getFunction()->getName() == other.node->getFunction()->getName()) {
      return true;
    }
  }
  return false;
}

llvm::CallGraphNode* ExtendedCGNode::getNode() {
  return node;
}

void ExtendedCGNode::setPredecessor(llvm::CallGraphNode *predecessor) {
  pred = predecessor;
}

std::string ExtendedCGNode::getFnName() const {
  return node->getFunction() ? node->getFunction()->getName() : "null";
}
