#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;

namespace {
struct ShortestPathPass : public FunctionPass {
  static char ID;
  ShortestPathPass() : FunctionPass(ID) {}

  bool runOnFunction(Function &F) override {
    errs() << "Hello: ";
    errs().write_escaped(F.getName()) << '\n';
    return false;
  }
}; // end of struct Hello
}  // end of anonymous namespace

char ShortestPathPass::ID = 0;
static RegisterPass<ShortestPathPass> X("shortestPath", "Shortest Path Pass",
                             false /* Only looks at CFG */,
                             false /* Analysis Pass */);