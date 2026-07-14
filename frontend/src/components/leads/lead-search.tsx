interface Props {
  value: string;
  onChange: (
    value: string
  ) => void;
}

export function LeadSearch({
  value,
  onChange,
}: Props) {
  return (
    <input
      className="w-full rounded-lg border px-4 py-2"
      placeholder="Search leads..."
      value={value}
      onChange={(e) =>
        onChange(e.target.value)
      }
    />
  );
}