import Lean.Data.Json
import Std.Data.HashSet
import Std.Data.HashMap

namespace SFTValidation

open Lean

def exceptToIO {α : Type} (context : String) (value : Except String α) : IO α :=
  match value with
  | .ok result => pure result
  | .error message => throw <| IO.userError s!"{context}: {message}"

def readJson (path : System.FilePath) : IO Json := do
  let contents ← IO.FS.readFile path
  exceptToIO s!"invalid JSON at {path}" (Json.parse contents)

def field (json : Json) (name : String) : Except String Json :=
  json.getObjVal? name

def stringField (json : Json) (name : String) : Except String String := do
  let value ← field json name
  value.getStr?

def natField (json : Json) (name : String) : Except String Nat := do
  let value ← field json name
  value.getNat?

def boolField (json : Json) (name : String) : Except String Bool := do
  let value ← field json name
  value.getBool?

def arrayField (json : Json) (name : String) : Except String (Array Json) := do
  let value ← field json name
  value.getArr?

def optionalField (json : Json) (name : String) : Option Json :=
  let value := json.getObjValD name
  if value.isNull then none else some value

def optionalStringField (json : Json) (name : String) : Except String (Option String) := do
  match optionalField json name with
  | none => pure none
  | some value => pure <| some (← value.getStr?)

def optionalBoolField (json : Json) (name : String) : Except String (Option Bool) := do
  match optionalField json name with
  | none => pure none
  | some value => pure <| some (← value.getBool?)

def stringsFromArray (values : Array Json) : Except String (Array String) := do
  let mut result := #[]
  for value in values do
    result := result.push (← value.getStr?)
  pure result

def stringArrayField (json : Json) (name : String) : Except String (Array String) := do
  stringsFromArray (← arrayField json name)

def optionalStringArrayField (json : Json) (name : String) : Except String (Option (Array String)) := do
  match optionalField json name with
  | none => pure none
  | some value => pure <| some (← stringsFromArray (← value.getArr?))

def nonemptyString (value : String) : Bool :=
  !value.isEmpty

def sha256Identity (value : String) : Bool :=
  value.startsWith "sha256:" && value.length = 71

def jsonBoolOr (json : Json) (name : String) (default : Bool) : Bool :=
  match optionalField json name with
  | some (.bool value) => value
  | _ => default

def jsonArrayEmptyOrMissing (json : Json) (name : String) : Bool :=
  match optionalField json name with
  | none => true
  | some (.arr values) => values.isEmpty
  | _ => false

def sameStringSet (left right : Std.HashSet String) : Bool :=
  left.size == right.size && left.toArray.all fun value => right.contains value

end SFTValidation
