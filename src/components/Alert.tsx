const Alert = (props) => {
	return (
		<div className={`${props.myclassName} alert`}>
			<h4>{props.content} !!!!</h4>
		</div>
	)
};
export default Alert