#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Analysis/CallGraph.h"
#include "llvm/Analysis/CallGraphSCCPass.h"

using namespace llvm;

namespace {
struct ShortestPathPass : public CallGraphSCCPass {
  static char ID;
  ShortestPathPass() : CallGraphSCCPass(ID) {}

  bool runOnSCC(CallGraphSCC &SCC) override {
    errs() << "Size = " << SCC.size();

    for (auto const &it = SCC.begin(); it != SCC.end(); it++) {
      
    }

    return false;
  }
}; // end of struct Hello
}  // end of anonymous namespace

char ShortestPathPass::ID = 0;
static RegisterPass<ShortestPathPass> X("shortestPath", "Shortest Path Pass",
                             false /* Only looks at CFG */,
                             false /* Analysis Pass */);