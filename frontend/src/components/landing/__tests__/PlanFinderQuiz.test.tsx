// @vitest-environment jsdom
import { describe, it, expect, vi, afterEach, beforeAll } from "vitest";
import { fireEvent, render, screen, cleanup, waitFor } from "@testing-library/react";
import { PlanFinderQuiz } from "../PlanFinderQuiz";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

beforeAll(() => {
  Element.prototype.scrollIntoView = () => {};
});

async function finishQuizWithBudget() {
  const goal = screen.getByRole("button", { name: /Scale outreach & leads/i });
  fireEvent.click(goal);
  const team = screen.getByRole("button", { name: /2–10 people/i });
  fireEvent.click(team);
  const budget = screen.getByRole("button", { name: /\$30–\$150/i });
  fireEvent.click(budget);
  await waitFor(() => screen.getByText(/Genesis Growth/i));
}

describe("PlanFinderQuiz lead capture honesty", () => {
  it("does not claim saved when the capture request fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));
    render(<PlanFinderQuiz />);
    await finishQuizWithBudget();

    fireEvent.change(screen.getByLabelText("Email address"), { target: { value: "founder@example.com" } });
    fireEvent.click(screen.getByRole("button", { name: /Unlock plan/i }));

    await waitFor(() => {
      expect(screen.queryByText(/Saved! We'll send your setup steps/i)).toBeNull();
    });
    expect(screen.getByText(/Couldn't save that.*try again/i)).toBeTruthy();
  });

  it("shows the saved confirmation only on a successful capture", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ created: true, lead_id: "L1", email: "founder@example.com" }),
      })
    );
    render(<PlanFinderQuiz />);
    await finishQuizWithBudget();

    fireEvent.change(screen.getByLabelText("Email address"), { target: { value: "founder@example.com" } });
    fireEvent.click(screen.getByRole("button", { name: /Unlock plan/i }));

    await waitFor(() => {
      expect(screen.getByText(/Saved! We'll send your setup steps/i)).toBeTruthy();
    });
    expect(screen.queryByText(/Couldn't save that/i)).toBeNull();
  });
});