"use client";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

import {
  useCreateCheckoutSession,
} from "@/hooks/use-create-checkout-session";

interface Props {
  name: string;

  price: string;

  amountCents: number;

  description: string;

  features?: string[];
}

export function PricingCard({
  name,
  price,
  amountCents,
  description,
  features = [],
}: Props) {
  const checkout =
    useCreateCheckoutSession();

  async function handleCheckout() {
    try {
      const session =
        await checkout.mutateAsync(
          {
            product_name:
              name,

            amount_cents:
              amountCents,
          }
        );

      if (
        session?.url
      ) {
        window.location.assign(
          session.url
        );
      }
    } catch (error) {
      console.error(
        "Checkout failed",
        error
      );
    }
  }

  return (
    <Card className="flex h-full flex-col p-6">
      <div>
        <h2 className="text-xl font-semibold">
          {name}
        </h2>

        <div className="mt-4 text-4xl font-bold">
          {price}
        </div>

        <p className="mt-4 text-sm text-muted-foreground">
          {description}
        </p>
      </div>

      {features.length >
        0 && (
        <div className="mt-6 flex-1">
          <ul className="space-y-2 text-sm">
            {features.map(
              (
                feature
              ) => (
                <li
                  key={
                    feature
                  }
                >
                  • {feature}
                </li>
              )
            )}
          </ul>
        </div>
      )}

      <Button
        className="mt-6 w-full"
        onClick={
          handleCheckout
        }
        disabled={
          checkout.isPending
        }
      >
        {checkout.isPending
          ? "Creating Session..."
          : "Subscribe"}
      </Button>
    </Card>
  );
}