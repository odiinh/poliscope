import { expect, test } from "vitest";
import { verifyDims } from "./verify";

// same case as pipeline/extract/test_verify.py
const SOURCE = "We will  cut the income tax\nto 4 percent — starting now. Schools matter.";

test("verifyDims keeps only exact quotes and nulls unsupported dimensions", () => {
  const { dims, kept, given } = verifyDims(
    {
      tax: {
        stance: 0.8,
        salience: 1,
        confidence: 1,
        evidence: ["cut the income tax to 4 percent - starting now.", "We will raise taxes."],
      },
      education: { stance: -0.5, salience: 0.5, confidence: 0.5, evidence: ["Schools are great."] },
      health: { stance: null, salience: 0, confidence: 0, evidence: [] },
    },
    SOURCE,
  );
  expect([kept, given]).toEqual([1, 3]);
  expect(dims.tax.evidence).toEqual(["cut the income tax to 4 percent - starting now."]);
  expect(dims.education).toEqual({ stance: null, salience: 0, confidence: 0, evidence: [] });
  expect(dims.health.stance).toBeNull();
});
