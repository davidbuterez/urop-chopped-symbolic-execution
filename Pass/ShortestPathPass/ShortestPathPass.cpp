#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Analysis/CallGraph.h"
#include "llvm/Analysis/CallGraphSCCPass.h"
#include "GraphManager.h"

using namespace llvm;

namespace {
struct ShortestPathPass : public CallGraphSCCPass {
  static char ID;
  ShortestPathPass() : CallGraphSCCPass(ID) {}

  bool runOnSCC(CallGraphSCC &SCC) override {
    // errs() << "Current SCC:" << &SCC << '\n';

    // for (CallGraphSCC::iterator it = SCC.begin(); it != SCC.end(); it++) {
    //   CallGraphNode *const node = *it;
    //   node->dump();
    // }

    GraphManager graphManager {SCC};

    return false;
  }
}; // end of struct Hello
}  // end of anonymous namespace

char ShortestPathPass::ID = 0;
static RegisterPass<ShortestPathPass> X("shortestPath", "Shortest Path Pass",
                             false /* Only looks at CFG */,
                             false /* Analysis Pass */);