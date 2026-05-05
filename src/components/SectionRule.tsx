export default function SectionRule({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-4 mt-14 mb-7">
      <span className="smallcaps text-primary whitespace-nowrap">{label}</span>
      <span className="flex-1 bg-rule" style={{ height: "0.5px" }} />
    </div>
  );
}
