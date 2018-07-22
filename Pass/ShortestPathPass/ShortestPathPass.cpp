#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Analysis/CallGraph.h"
#include "llvm/Analysis/CallGraphSCCPass.h"
#include "llvm/Support/CommandLine.h"
#include "GraphManager.h"

using namespace llvm;

static cl::opt<std::string> Target("target", cl::desc("Specify target function"), cl::value_desc("target"));

namespace llvm {
struct ShortestPathPass : public CallGraphSCCPass {
  static char ID;
  ShortestPathPass() : CallGraphSCCPass(ID) {}

  bool runOnSCC(CallGraphSCC &SCC) override {
    // GraphManager graphManager = GraphManager(SCC);
    // auto targetNode = graphManager.findTargetNode(Target.c_str());
    // auto path = graphManager.getShortestPath(targetNode);
    // graphManager.printPath(path);
    

    // for (CallGraphSCC::iterator it = SCC.begin(); it != SCC.end(); it++) {
    //   CallGraphNode *const node = *it;
    //   if (node->getFunction()) {
    //     errs() << node->getFunction()->getName();
    //   }
    // }
    return false;
  }

  bool doInitialization(CallGraph &CG) override {
    GraphManager graphManager {CG};
    auto targetNode = graphManager.findTargetNode(Target.c_str());
    auto path = graphManager.getShortestPath(targetNode);
    graphManager.printPath(path);
  }
}; // end of struct ShortestPathPass
}  // end of anonymous namespace

char ShortestPathPass::ID = 0;
static RegisterPass<ShortestPathPass> X("shortestPath", "Shortest Path Pass",
                             false /* Only looks at CFG */,
                             false /* Analysis Pass */);