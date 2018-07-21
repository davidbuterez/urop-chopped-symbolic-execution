#ifndef EXTENDEDCGNODE_H
#define EXTENDEDCGNODE_H

#include <limits>
#include "llvm/Analysis/CallGraph.h"

class ExtendedCGNode {
  public:
    // Constructors
    ExtendedCGNode();

    ExtendedCGNode(llvm::CallGraphNode *node, llvm::CallGraphNode *pred, unsigned distance);

    bool operator== (const ExtendedCGNode &node) const;  

    llvm::CallGraphNode* getNode();
  
    void setPredecessor(llvm::CallGraphNode *predecessor);
    
    std::string getFnName() const;
  

  private:
    llvm::CallGraphNode *node;
    llvm::CallGraphNode *pred;
    unsigned distance;
};

namespace std {
  template<>
    struct hash<ExtendedCGNode*> {
      size_t operator()(const ExtendedCGNode* &other) const {
        return hash<std::string>()(other->getFnName());
      }
    };
}

#endif /* EXTENDEDCGNODE_H */
