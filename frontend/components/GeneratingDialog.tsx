// components/GeneratingDialog.tsx
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Loader2 } from "lucide-react";

type Props = {
  open: boolean;
};

export default function GeneratingDialog({ open }: Props) {
  return (
    <Dialog open={open}>
      <DialogContent className="flex flex-col items-center justify-center text-center gap-4">
        <DialogHeader>
          <DialogTitle>Generating your article...</DialogTitle>
        </DialogHeader>
        <Loader2 className="animate-spin w-6 h-6 text-primary" />
        <p className="text-muted-foreground text-sm">
          Please wait while our AI writes your content.
        </p>
      </DialogContent>
    </Dialog>
  );
}
