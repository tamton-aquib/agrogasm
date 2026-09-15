interface AlertProps {
  myclassName: string;
  content: string;
}

const Alert = ({ myclassName, content }: AlertProps) => {
	return (
		<div className={`${myclassName} alert`}>
			<h4>{content}</h4>
		</div>
	)
};
export default Alert
