#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/PassManager.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Analysis/CallGraph.h"
#include "llvm/Analysis/CallGraphSCCPass.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/Support/MemoryBuffer.h"
#include "llvm/Support/SourceMgr.h"
#include "llvm/Support/ErrorOr.h"
#include "llvm/IR/LLVMContext.h"
#include "llvm/Bitcode/ReaderWriter.h"
#include "llvm/IR/Module.h"
#include "llvm/Analysis/Verifier.h"
#include "GraphManager.h"
#include "llvm/IRReader/IRReader.h"

using namespace llvm;

static cl::opt<std::string> Bitcode("file");
static cl::opt<std::string> Target("target", cl::desc("Specify target function"), cl::value_desc("target"));

namespace {
  std::vector<std::string> getFunctionsFromBitcode() {
    LLVMContext context;
    SMDiagnostic error;

    Module *module = ParseIRFile(StringRef(Bitcode), error, context);
    
    if (!module) {
      errs() << "Couldn't get module frum file " << Bitcode << "\n";
    }

    verifyModule(*module);

    std::vector<std::string> allFunctions;
    
    for (Function &F : *module) {
      allFunctions.push_back(F.getName());
    }

    return allFunctions;
  }
}

namespace llvm {
struct ShortestPathPass : public CallGraphSCCPass {
  static char ID;
  ShortestPathPass() : CallGraphSCCPass(ID) {}

  bool runOnSCC(CallGraphSCC &SCC) override {
    return false;
  }

  bool doInitialization(CallGraph &CG) override {
    auto allFunctions = getFunctionsFromBitcode();

    GraphManager graphManager {CG};
    auto targetNode = graphManager.findTargetNode(Target.c_str(), allFunctions);
    graphManager.getShortestPath(targetNode);
    graphManager.excludeSelective();
    // graphManager.excludeAll();

    return false;
  }
}; // end of struct ShortestPathPass
}  // end of anonymous namespace

char ShortestPathPass::ID = 0;
static RegisterPass<ShortestPathPass> X("shortestPath", "Shortest Path Pass",
                             false /* Only looks at CFG */,
                             false /* Analysis Pass */);                          