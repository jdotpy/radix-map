package radix.test.fixtures

import scala.annotation.tailrec

// ==========================================
// 1. STANDARD STRUCTURE WITH SCALA 3 REGIONS
// ==========================================
class DataProcessor(val engineId: String):
  def process(data: String): Boolean =
    println(s"Processing $data")
    true

  def noBracesMethod: Unit =
    val localX = 10
    println(localX)

// ==========================================
// 2. MIXED NESTING & TRICKY EXTENSIONS
// ==========================================
object Router:
  // A trait inside an object template body
  trait Endpoint:
    def routePath: String
    def handler(req: String): String

  // Deeply nested anonymous functions and Scala 3 context structures
  def buildRoute(using ctx: String)(path: String)(inline filter: String => Boolean): Endpoint =
    new Endpoint:
      def routePath: String = path
      def handler(req: String): String = 
        // Nested local definition inside a method body (should NOT be classified as top-level or method definition)
        def innerHelper(s: String): String = s.reverse
        if filter(req) then innerHelper(req) else "filtered"

  // Empty parameter list vs omitted parameter list
  def noParams(): Unit = ()
  def omittedParams: Unit = ()

// ==========================================
// 3. MULTI-LINE DEFINITIONS & BACKTICKS
// ==========================================
trait ComplexSignatures:
  // Extreme multi-line method signature to test spacing and capture resilience
  def executeTransaction(
    sourceAccount: String,
    targetAccount: String,
    amount: BigDecimal,
    bypassValidation: Boolean = false
  )(using context: String): Option[String]

  // Backticks allowing reserved keyword names as identifiers
  def `match`(`type`: String): Boolean = `type` == "match"

// ==========================================
// 4. SCALA 3 ADDS, ENUMS, & TOP-LEVEL ITEMS
// ==========================================
enum ProtocolKind:
  case Http, Https, Gql

// Top-level value definitions (legal in Scala 3, tests your global variables parser)
val GlobalConfigKey: String = "RADIX_TEST_SECRET_ABC123"
var mutableGlobalCounter: Int = 0

// A true top-level function outside of any class or object scope
def packageLevelUtility(input: Int): Int =
  input * 42