import SFTValidation.Root
import SFTValidation.Verifier

open SFTValidation

def usage : String :=
  "usage: sft-verify <repository-root> <report-path>"

def main (arguments : List String) : IO UInt32 := do
  match arguments with
  | [root, report] =>
    try
      let passed ← runWholeModelVerification ⟨root⟩ ⟨report⟩
      pure <| if passed then 0 else 1
    catch error =>
      IO.eprintln s!"LEAN SFT WHOLE-MODEL VERIFICATION: HALTED: {error}"
      pure 2
  | _ =>
    IO.eprintln usage
    pure 2
