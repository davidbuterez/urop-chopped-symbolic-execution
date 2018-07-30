#include <iostream>
#include "llvm/Pass.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/Function.h"
#include "llvm/PassManager.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Support/CommandLine.h"

using namespace llvm;

static cl::list<std::string> ShortestPath("path", cl::desc("Functions on the shortest path"), cl::value_desc("path"), cl::CommaSeparated);

namespace llvm {
struct SkipFunctionsPass : public ModulePass {
  static char ID;
  SkipFunctionsPass() : ModulePass(ID) {}

  bool runOnModule(Module &M) override {
    // Output functions which are not on the path
    for (auto curr = M.begin(); curr != M.end(); ++curr) {
      if (std::find(ShortestPath.begin(), ShortestPath.end(), curr->getName().str()) != ShortestPath.end()) {
        continue;
      }
      std::cout << curr->getName().str() << ",";
    }
    return false;
  }

}; // end of struct SkipFunctionsPass
}  // end of anonymous namespace

char SkipFunctionsPass::ID = 1;
static RegisterPass<SkipFunctionsPass> X("skipFunctions", "What functions to skipx",
                             false /* Only looks at CFG */,
                             false /* Analysis Pass */);