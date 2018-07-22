#ifndef EXTENDEDCGNODE_H
#define EXTENDEDCGNODE_H

#include <limits>
#include "llvm/Analysis/CallGraph.h"

class ExtendedCGNode {
  friend class GraphManager;

  public:
    ExtendedCGNode();

    ExtendedCGNode(llvm::CallGraphNode *node, std::shared_ptr<ExtendedCGNode> pred, unsigned distance);
      
    std::string getFnName() const;

  private:
    llvm::CallGraphNode *node;
    std::shared_ptr<ExtendedCGNode> pred;
    unsigned distance;
};

struct ExtendedNodeHasher {
  size_t operator() (std::shared_ptr<ExtendedCGNode> const ptr) const {
    return std::hash<std::string>()(ptr->getFnName());
  }
};

struct ExtendedNodeEq {
  size_t operator() (std::shared_ptr<ExtendedCGNode> const a, std::shared_ptr<ExtendedCGNode> const b) const {
    return a->getFnName() == b->getFnName();
  }
};

#endif /* EXTENDEDCGNODE_H */
